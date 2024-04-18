from fastapi.security import OAuth2PasswordBearer
from insightscapehub.utils import settings
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.APP_PREFIX + '/token' if settings.APP_PREFIX else '/accounts/toke/')
pwd_context = CryptContext(schemes=['bcrypt'])
