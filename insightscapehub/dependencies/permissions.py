from fastapi import Depends, HTTPException, Request, status, Header
from insightscapehub.utils.db import Session, get_db
from insightscapehub.crud.auth import get_user
from insightscapehub.security.context import oauth2_scheme
from insightscapehub.utils.exceptions import UserUnauthenticated
from insightscapehub.utils.helpers import decode_token


def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token, force_access=True)
    user_id: str = payload.get("user_id")
    return user_id


async def get_auth_user(current_user: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = get_user(db, current_user)
    if user is None:
        raise UserUnauthenticated
    return user
