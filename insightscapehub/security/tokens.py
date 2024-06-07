from insightscapehub.utils.db import Session, get_db
from insightscapehub.models.user import User
from insightscapehub.crud.auth import get_one
from insightscapehub.utils.helpers import (
    create_access_token, create_refresh_token, get_session_id_for_user, decode_token)
from uuid import UUID
import base64


class AccessTokens:
    header = 'Authorization'

    @classmethod
    def __init__(self, user: User):
        session_id = get_session_id_for_user(user)
        db: Session = next(get_db())

        user_info = f"{user.username},{user.email}"
        self.access_token = create_access_token(user, session_id, user_info)
        self.refresh_token = create_refresh_token(user, session_id)
        self._user = {
            'status': user.status,
            'id': user.id,
            'email': user.email
        }

        db.close()

    def __str__(self) -> str:
        return self.access_token

    def toJSON(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': 'bearer',
            'user': self._user
        }

    @classmethod
    def refresh_for_user(cls, refresh_token: str, db: Session):
        user_id = decode_token(
            refresh_token, force_refresh=True).get('user_id', None)

        user = get_one(user_id)

        return cls(user)

    def get_auth_header(self):
        return {self.header: f"Bearer {self.access_token}"}
