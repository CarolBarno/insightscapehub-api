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
