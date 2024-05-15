from typing import List
from insightscapehub.utils.db import Session
from insightscapehub.models.user import User
from insightscapehub.schemas.auth import RegisterInput
from insightscapehub.utils.depends import create_update_delete, get_records
from insightscapehub.models.user import User
from insightscapehub.schemas.auth import UserSchema


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email.like(email.strip())).first()


def create_user(db: Session, data: RegisterInput):
    try:
        res = create_update_delete(User, db, data, 'create', {
                                   'email': data.email}, UserSchema)
        return res
    except Exception as e:
        raise e


def get_all(db: Session, pagination_params: dict) -> List[UserSchema]:
    return get_records(User, db, pagination_params, {}, UserSchema)
