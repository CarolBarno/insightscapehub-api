from typing import Annotated, Optional, List
from pydantic import UUID4, BaseModel, EmailStr
from insightscapehub.schemas.response import PageInfo
from insightscapehub.utils.enums import Status


class RegisterInput(BaseModel):
    email: EmailStr
    username: Optional[str] = None

    class Config:
        from_attributes = True
        frozen = True


class UserSchema(BaseModel):
    id: Annotated[UUID4, str]
    username: Optional[str]
    email: Optional[EmailStr]
    status: Annotated[Status, str]

    class Config:
        from_attributes = True
        frozen = True


class QueryResp(BaseModel):
    results: List[UserSchema]
    page_info: PageInfo
