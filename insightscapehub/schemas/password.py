from typing import Union
from pydantic import BaseModel, EmailStr, Field, SecretStr

from insightscapehub.schemas.base import BasePasswordField
from insightscapehub.utils.enums import VerificationType


class RequestPasswordReset(BaseModel):
    username: Union[EmailStr, str] = Field(
        description="User's email or username"
    )


class PasswordResetChangeInput(BasePasswordField):
    token: str = Field(
        description="The token that was sent to email"
    )


class PasswordChangeInput(BasePasswordField):
    current_password: SecretStr = Field(
        description="The user's initial password")
