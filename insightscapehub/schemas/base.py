from pydantic import BaseModel, Field, SecretStr, field_validator
from insightscapehub.utils.validators import PASSWORD_DESCRIPTION, is_valid_password


class BasePasswordField(BaseModel):
    password: SecretStr = Field(description=PASSWORD_DESCRIPTION)

    @field_validator('password')
    def validate_password(cls, value: SecretStr):
        is_valid_password(password=value.get_secret_value())

        return value.get_secret_value()
