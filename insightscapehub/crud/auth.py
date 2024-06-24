from typing import List
import uuid
from insightscapehub.utils.db import Session
from insightscapehub.models.user import User
from insightscapehub.schemas.auth import RegisterInput
from insightscapehub.utils.depends import create_update_delete, get_records
from insightscapehub.models.user import User
from insightscapehub.schemas.auth import UserSchema
from sqlalchemy import or_

from insightscapehub.utils.exceptions import HTTPNotItemFound


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


def get_one(db: Session, id: str) -> UserSchema:
    user = get_records(User, db, {}, {id}, UserSchema)
    if user:
        return user[0]
    else:
        raise HTTPNotItemFound()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username.like(username.strip())).first()


def get_user_by_username_or_email(db: Session, username: str, *extra_filters):
    return (
        db.query(User)
        .filter(
            or_(
                User.email.ilike(username.strip()),
                User.username.ilike(username.strip())),
            *extra_filters
        )
        .first()
    )

def get_user(db: Session, user_id: uuid.UUID):
    return db.query(User).get(user_id)