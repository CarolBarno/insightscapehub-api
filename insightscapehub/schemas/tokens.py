from pydantic import BaseModel, Field


class RefreshTokenInput(BaseModel):
    refresh_token: str = Field(description='The obtained access token')


class AuthTokenResponse(RefreshTokenInput):
    access_token: str = Field(description='The access token header')
    token_type: str = Field(
        'bearer', description='The access token header type')

    class Config:
        from_attributes = True
