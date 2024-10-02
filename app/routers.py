from fastapi.routing import APIRouter
from insightscapehub.utils.enums import APITags
from fastapi import Depends
from insightscapehub.dependencies.permissions import get_auth_user

auth_deps = [Depends(get_auth_user)]

auth_router = APIRouter(prefix="/users", tags=[APITags.user])
password_router = APIRouter(prefix="/password", tags=[APITags.password])
verify_router = APIRouter(prefix="/verify", tags=[APITags.verification])
