from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field

class Info(BaseModel):
    version: str
    last_supported_version: str

class User(BaseModel):
    username: str
    mail: str

    class Config:
        orm_mode = True

class UserResponse(User):
    user_id: int
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

class Chat(BaseModel):
    user_id: int
    name: str
    is_muted: bool
    is_archived: bool
    pin_position: Optional[int]

    # last message

    class Config:
        orm_mode = True

class ChatResponse(Chat):
    chat_id: int

class Pin(BaseModel):
    pin_position: int