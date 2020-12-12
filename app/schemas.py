from datetime import datetime
from pydantic import BaseModel
from pydantic.fields import Field

class Info(BaseModel):
    version: str
    last_supported_version: str

class User(BaseModel):
    user_id: int
    username: str
    mail: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class AuthUser(User):
    hashed_password: str

class RegisterRequest(User):
    password: str

class VerifyRequest(BaseModel):
    username: str
    verification_code: str = Field(min_length=6, max_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str