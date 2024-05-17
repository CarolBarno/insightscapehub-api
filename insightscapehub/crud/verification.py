import hashlib
from datetime import datetime, timezone
from insightscapehub.utils.db import Session
from insightscapehub.models.verification import (
    VerificationToken, VerificationTokenStatus, VerificationType)
from insightscapehub.models.user import User


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
        extra.append(VerificationToken.status != VerificationTokenStatus.value)

    return (db.query(VerificationToken).filter(*extra, VerificationToken.token == token).first())


def set_token_as_used(token: VerificationToken):
    token.status = VerificationTokenStatus.USED.value
    token.expiry = datetime.now(timezone.utc)

    return token
