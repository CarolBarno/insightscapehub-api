from fastapi.routing import APIRouter
from insightscapehub.utils.enums import APITags

auth_router = APIRouter(tags=[APITags.user])