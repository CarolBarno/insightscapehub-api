from app.routers import auth_router
from fastapi import status, Depends
from insightscapehub.schemas.auth import (UserSchema, RegisterInput, QueryResp)
from insightscapehub.crud.auth import (create_user, get_all)
from insightscapehub.utils.db import get_db, Session
from insightscapehub.utils.depends import extract_pagination_params


@auth_router.get(
    '/',
    response_model=QueryResp,
    response_description="List of all users")
async def get_users(
        db: Session = Depends(get_db),
        pagination_params: dict = Depends(extract_pagination_params)):
    return get_all(db, pagination_params)


@auth_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    summary='Add a User',
    response_model=UserSchema
)
def add_user(data: RegisterInput, db: Session = Depends(get_db)):
    return create_user(db, data)
