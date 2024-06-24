import hashlib
from typing import Callable
from datetime import datetime, timezone
from fastapi import BackgroundTasks
from insightscapehub.utils.db import Session
from insightscapehub.models.verification import (
    VerificationToken, VerificationTokenStatus, VerificationType)
from insightscapehub.models.user import User
from insightscapehub.utils.exceptions import TokenNotFound
from insightscapehub.schemas.verification import VerificationTokenSafeResponse, InitialVerificationInput
from app.tasks import send_reg_email, send_reset_password
from insightscapehub.utils.enums import Status


def generate_verification_token_for_user(user: User):
    if not user:
        return None
    return hashlib.sha1(f'{user.id}{datetime.now()}'.encode()).hexdigest()


def create_token_for_user(user: User, token_type=VerificationType.INITIAL_VERIFICATION):
    token = VerificationToken()
    token.user_id = user.id
    token.type = token_type
    token.token = generate_verification_token_for_user(user)
    return token


def get_token_by_token_str(db: Session, token: str, safe=True) -> VerificationToken | None:
    extra = []
    if safe:
        extra.append(VerificationToken.expiry > datetime.now(timezone.utc))
        extra.append(VerificationToken.status !=
                     VerificationTokenStatus.USED.value)

    return (db.query(VerificationToken).filter(*extra, VerificationToken.token == token).first())


def set_token_as_used(token: VerificationToken):
    token.status = VerificationTokenStatus.USED.value
    token.expiry = datetime.now(timezone.utc)

    return token


def get_token(token: str, get_token: any):
    token_from_db = get_token(token, safe=False)

    if not token_from_db:
        TokenNotFound

    return VerificationTokenSafeResponse.model_validate(token_from_db)


def request_verification(token: str, bg: BackgroundTasks, get_extend_token: Callable):
    db_token: VerificationToken = get_extend_token(token)

    if not db_token:
        raise TokenNotFound

    if db_token.type == VerificationType.INITIAL_VERIFICATION.value:
        bg.add_task(send_reg_email, db_token.user, db_token)
    elif db_token.type == VerificationType.PASSWORD_RESET:
        bg.add_task(send_reset_password, db_token)


def verify_token(token: str, data: InitialVerificationInput, db: Session, get_token: any):
    db_token: VerificationToken = get_token(token, safe=True)

    if not db_token:
        raise TokenNotFound

    user: User = db_token.user

    if user:
        user.set_password(data.password)
        user.username = getattr(data, "username", user.username)
        user.status = Status.ACTIVE

        db.add(user)

    db_token = set_token_as_used(db_token)

    db.add(db_token)
    db.commit()

    return VerificationTokenSafeResponse.model_validate(db_token)
