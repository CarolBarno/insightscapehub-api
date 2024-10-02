from fastapi import BackgroundTasks, HTTPException
from typing import Callable
from insightscapehub.utils.db import Session
from insightscapehub.schemas.password import RequestPasswordReset, PasswordResetChangeInput, PasswordChangeInput
from insightscapehub.utils.exceptions import UserNotFound
from insightscapehub.crud.auth import get_user_by_username_or_email
from insightscapehub.crud.verification import set_token_as_used
from insightscapehub.models.user import User
from insightscapehub.models.verification import VerificationToken, VerificationType
from insightscapehub.utils.enums import Status
from insightscapehub.schemas.verification import VerificationTokenSafeResponse
from insightscapehub.schemas.auth import UserSchema
from app.tasks import send_reset_password
from insightscapehub.dependencies.verification import GetTokenObj


def request_password_reset(
    db: Session,
    data: RequestPasswordReset,
    bg: BackgroundTasks,
    create_token: Callable[[User, VerificationType], VerificationToken]
):
    username = data.model_dump().get("username", None)

    if not username:
        raise UserNotFound()

    user = get_user_by_username_or_email(
        db, username, User.status == Status.ACTIVE)

    if not user:
        raise UserNotFound()

    token: VerificationToken = create_token(
        user, VerificationType.PASSWORD_RESET)

    db.add(token)
    db.commit()

    bg.add_task(send_reset_password, token)

    return VerificationTokenSafeResponse.model_validate(token)


def reset_password(
    data: PasswordResetChangeInput,
    get_token: GetTokenObj,
    db: Session
):
    data_json = data.model_dump()
    token: VerificationToken = get_token(data_json.get("token"), True)

    if (not token or token.type != VerificationType.PASSWORD_RESET or not token.user):
        raise HTTPException(404, "Token not found or is expired")

    user: User = token.user
    user.set_password(data_json.get("password"))

    token = set_token_as_used(token)

    db.add_all([user, token])
    db.commit()

    return VerificationTokenSafeResponse.model_validate(token)


def change_password(
    data: PasswordChangeInput,
    user: User,
    db: Session
):
    if not user.check_password(data.current_password.get_secret_value()):
        raise HTTPException(
            400, {"password": "The credentials provided did not match"})

    user = user.set_password(data.password)

    db.add(user)
    db.commit()

    return UserSchema.model_validate(user)
