from jose import exceptions, jwt
from insightscapehub.utils import settings
from insightscapehub.utils.exceptions import UserUnauthenticated
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from typing import LiteralString, TypedDict
from insightscapehub.crud.auth import get_user_by_username_or_email
from insightscapehub.utils.enums import Status
from insightscapehub.models.user import User
from insightscapehub.utils.exceptions import (
    UserInactive, UserNotFound, UserNotVerified, UserUnauthenticated)
from insightscapehub.security.hashing import verify_password
import base64
from starlette.datastructures import UploadFile
from urllib.parse import urlparse
from io import BytesIO
import requests


def decode_token(token, force_access=True, force_refresh=False, secret_key: str = settings.SECRET_KEY, algorithms=[settings.ALGORITHM]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        _type = payload.get('type', None)

        if (_type != 'access' and force_access and not force_refresh) or (_type != 'refresh' and force_refresh):
            raise UserUnauthenticated

        return payload
    except exceptions.ExpiredSignatureError:
        raise UserUnauthenticated
    except exceptions.JWTError:
        raise UserUnauthenticated


def get_session_id_for_user(user: User) -> str:
    now = datetime.now(timezone.utc).timestamp()
    content = f"{user.id}-{now}".encode()

    return sha1(content).hexdigest()


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username_or_email(db, username)
    if not user:
        raise UserNotFound

    if user.status == Status.PENDING:
        raise UserNotVerified

    if user.status == Status.INACTIVE:
        raise UserInactive

    if (not verify_password(password, user.password) or user.status != Status.ACTIVE):
        raise UserNotFound
    return user


def create_access_token(user: User, session_id: str, user_info: bytes = None):
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if user_info:
        user_info = base64.b64encode(user_info).decode('utf-8')

        to_encode = {
            'user_id': str(user.id),
            'exp': expire,
            'type': 'access',
            'session_id': session_id,
            'user_info': user_info
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt


def create_refresh_token(user: User, session_id: str):

    expire = datetime.now(timezone.utc) + timedelta(hours=24*30)
    to_encode = {
        'user_id': str(user.id),
        'exp': expire,
        'type': 'refresh',
        'session_id': session_id
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_extensions_from_env(env_variable_name):
    """
    Retrieves a set of file extensions from the environment variable.

    Args:
    env_variable_name (str): The name of the environment variable to fetch.

    Returns:
    set: A set of extensions with a leading '.' for each.
    """
    return {f'.{ext.strip()}' for ext in env_variable_name.split(',') if ext.strip()}


async def process_form_data(form_data):
    """
    Processes form data, separating regular form fields from file uploads.

    Parameters:
    - form_data (dict): A dictionary containing form data, possibly including file uploads.

    Returns:
    - prepared_form_data (dict): A dictionary containing regular form fields.
    - files_data (dict): A dictionary containing file upload information, with keys as field names and values as tuples
                        containing filename, file content, and content type.

    Example Usage:
    ```python
    form_data = {'name': 'John Doe', 'avatar': <UploadFile>, 'resume': <UploadFile>}
    prepared_data, files_info = await process_form_data(form_data)
    ```
    """
    prepared_form_data = {}
    files_data = {}

    for key, value in form_data.items():
        if isinstance(value, UploadFile):
            file_content = await value.read()
            if len(file_content) == 0:
                value.file.seek(0)  # Reset file pointer and try again
                file_content = await value.read()
            files_data[key] = (value.filename, file_content,
                               value.content_type)
        elif isinstance(value, str) and is_valid_url(value) and is_url_file(value):
            _file = url_to_uploadfile(value)
            files_data[key] = (_file.filename, await _file.read(), _file.content_type)
        else:
            prepared_form_data[key] = value

    return prepared_form_data, files_data


def is_url_file(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def url_to_uploadfile(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return UploadFile(
                filename=image_url.split(
                    "/")[-1], file=BytesIO(response.content)
            )
        else:
            print("Failed to fetch image from URL. Status code:",
                  response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching image from URL:", e)
        return None
