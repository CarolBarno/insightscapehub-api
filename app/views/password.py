from typing import Callable
from fastapi import BackgroundTasks, Depends
from insightscapehub.utils.db import Session, get_db
from app.routers import password_router
from insightscapehub.schemas.verification import VerificationTokenSafeResponse
from insightscapehub.schemas.password import RequestPasswordReset, PasswordResetChangeInput, PasswordChangeInput
from insightscapehub.models.user import User
from insightscapehub.models.verification import VerificationToken, VerificationType
from insightscapehub.dependencies.verification import create_token_for_user, get_token_obj, GetTokenObj
from insightscapehub.dependencies.permissions import get_auth_user
from insightscapehub.crud.password import request_password_reset, change_password, reset_password


@password_router.post(
    "/reset/",
    status_code=201,
    responses={201: {"model": VerificationTokenSafeResponse}}
)
def password_reset_request(
    data: RequestPasswordReset,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    create_token: Callable[[User, VerificationType],
                           VerificationToken] = Depends(create_token_for_user)
):
    response = request_password_reset(db, data, bg, create_token)
    return response


@password_router.post(
    "/reset/change/",
    summary="Change Password - Reset"
)
def password_reset(
    data: PasswordResetChangeInput,
    get_token: GetTokenObj = Depends(get_token_obj),
    db: Session = Depends(get_db)
):
    response = reset_password(data, get_token, db)
    return response


@password_router.post(
    "/change/",
    responses={}
)
def password_change(
    data: PasswordChangeInput,
    user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    response = change_password(data, user, db)
    return response
