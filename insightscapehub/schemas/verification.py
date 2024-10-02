from datetime import datetime
from typing import Annotated, Optional, Union
from insightscapehub.utils.db import Session, get_db
from pydantic import UUID4, ConfigDict, BaseModel, EmailStr, Field, field_validator
from insightscapehub.crud.auth import get_user_by_username
from insightscapehub.utils.enums import VerificationTokenStatus, VerificationType
from insightscapehub.schemas.base import BasePasswordField
from insightscapehub.utils.validators import USERNAME_REGEX, is_valid_username_regex


class VerificationTokenSafeResponse(BaseModel):
    status: VerificationTokenStatus
    type: VerificationType
    expiry: datetime
    is_expired: bool = Field(computed=True)
    can_resend: bool = Field(computed=True)
    remaining_minutes: int = Field(computed=True)

    class Config(ConfigDict):
        from_attributes = True


class InitialVerificationInput(BasePasswordField):
    username: Optional[Annotated[str | None, None]] = Field(
        default=None, description=f"Optional. Must match {USERNAME_REGEX}")

    @field_validator('username')
    def validate_username(cls, value: str):
        if not value:
            return None

        value = value.strip().lower()
        valid = is_valid_username_regex(value)

        if not valid:
            raise ValueError('Enter a valid username')

        db: Session = next(get_db())
        user = get_user_by_username(db, value)

        db.close()

        if user:
            raise ValueError('Username is taken')

        return value

    class Config:
        json_schema_extra = {"example": {
            "username": None, "password": "*******"}}
