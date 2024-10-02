from insightscapehub.utils.db import Session, get_db
from fastapi import Depends
from typing import Callable, Optional, Union
from datetime import datetime, timedelta, timezone
from insightscapehub.crud import verification as crud
from insightscapehub.dependencies.host import get_original_host
from insightscapehub.utils.enums import VerificationType
from insightscapehub.models.user import User
from insightscapehub.models.verification import VerificationToken


def create_token_for_user(db: Session = Depends(get_db), host=Depends(get_original_host)):
    def create(user: User, token_type=VerificationType.INITIAL_VERIFICATION):
        token = crud.create_token_for_user(user, token_type)
        token.host = host

        db.add(token)
        db.commit()
        return token
    return create


GetTokenObj = Callable[[str, Optional[bool]], Union[VerificationToken, None]]


def get_token_obj(db: GetTokenObj = Depends(get_db)) -> Callable:
    def get(token, safe=False):
        _token: VerificationToken = crud.get_token_by_token_str(
            db, token, safe)

        return _token
    return get


def get_or_extend_token_life(db: Session = Depends(get_db)):
    def get(token):
        token_obj: VerificationToken = crud.get_token_by_token_str(
            db, token, False)

        if not token_obj or token_obj.remaining_minutes > 20 or token_obj.is_used:
            return token_obj

        if token_obj.remaining_minutes < 0:
            token_obj.expiry = datetime.now(
                timezone.utc) + timedelta(minutes=20)
        else:
            token_obj.expiry = token_obj.expiry + timedelta(minutes=20)

        db.add(token_obj)
        db.commit()

        return token_obj
    return get
