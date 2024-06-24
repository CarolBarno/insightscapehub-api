from app.routers import auth_router
from typing import Callable
from fastapi import BackgroundTasks, Depends, status
from insightscapehub.schemas.auth import (UserSchema, RegisterInput, QueryResp)
from insightscapehub.crud.auth import (create_user, get_all)
from insightscapehub.utils.db import get_db, Session
from insightscapehub.utils.depends import extract_pagination_params
from insightscapehub.dependencies.verification import create_token_for_user
from app.tasks import send_reg_email


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
def add_user(
    data: RegisterInput,
    tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    create_token: Callable = Depends(create_token_for_user)
):
    user = create_user(db, data)
    token = create_token(user)
    tasks.add_task(send_reg_email, user, token)
    return user
