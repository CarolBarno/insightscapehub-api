from typing import Dict
from fastapi import HTTPException, status


class HTTPNotItemFound(HTTPException):
    def __init__(
        self,
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Data Not Found",
        headers: Dict[str, str] = {},
    ) -> None:
        super().__init__(status_code, detail, headers)
