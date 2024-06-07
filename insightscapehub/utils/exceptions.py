from typing import Dict, Any
from fastapi import HTTPException, status


class HTTPNotItemFound(HTTPException):
    def __init__(
        self,
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Data Not Found",
        headers: Dict[str, str] = {},
    ) -> None:
        super().__init__(status_code, detail, headers)


class UserUnauthenticated(HTTPException):
    def __init__(self, detail='User not authenticated') -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail, headers={"WWW-Authenticate": "Bearer"})


class UserNotFound(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class UserNotVerified(Exception):
    def __init__(self, message="User not verified"):
        self.message = message
        super().__init__(self.message)


class UserInactive(Exception):
    def __init__(self, message="User inactive"):
        self.message = message
        super().__init__(self.message)
