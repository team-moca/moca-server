from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel
from pydantic.fields import Field


class Info(BaseModel):
    current_version: str
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


class MessageContent(BaseModel):
    type: str
    content: Optional[str]
    url: Optional[str]


class Message(BaseModel):
    contact_id: int
    message: MessageContent
    sent_datetime: datetime

    class Config:
        orm_mode = True


class MessageResponse(Message):
    message_id: int


class Chat(BaseModel):
    user_id: int
    name: str
    is_muted: bool
    is_archived: bool
    pin_position: Optional[int]

    class Config:
        orm_mode = True


class ChatResponse(Chat):
    chat_id: int
    last_message: Optional[MessageResponse]


class Pin(BaseModel):
    pin_position: int


class DeleteMessageRequest(BaseModel):
    delete_everywhere: bool


class Contact(BaseModel):
    service_id: str
    name: str
    username: str
    phone: str
    avatar: Optional[str]
    is_self: bool

    class Config:
        orm_mode = True


class ContactResponse(Contact):
    contact_id: int


class Connector(BaseModel):

    connector_type: str
    configuration: Optional[str]

    class Config:
        orm_mode = True

class ConnectorResponse(Connector):
    connector_id: int

class InitializeConnectorRequest(BaseModel):
    connector_type: str