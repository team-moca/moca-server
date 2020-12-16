from datetime import datetime
from enum import Enum
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


class AuthUser(UserResponse):
    hashed_password: str
    session_id: Optional[str]
    is_verified: bool


class RegisterRequest(User):
    password: str


class VerifyRequest(BaseModel):
    username: str
    verification_code: str = Field(min_length=6, max_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str

class MessageType(str, Enum):
    unsupported = 'unsupported'
    text = 'text'
    image = 'image'
    audio = 'audio'
    voice = 'voice'
    video = 'video'
    gif = 'gif'
    document = 'document'
    contact = 'contact'
    geo = 'geo'

class GeoPoint(BaseModel):
    lon: float
    lat: float

class MessageContent(BaseModel):
    type: MessageType
    content: Optional[str]
    url: Optional[str]
    geo_point: Optional[GeoPoint]


class Message(BaseModel):
    message: MessageContent

    class Config:
        orm_mode = True


class MessageResponse(Message):
    contact_id: int
    message_id: int
    sent_datetime: datetime


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
    username: Optional[str]
    phone: Optional[str]
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

class Session(BaseModel):
    name: Optional[str]
    valid_until: datetime

    class Config:
        orm_mode = True

class SessionResponse(Session):
    session_id: int

class Pagination(BaseModel):
    page: int
    count: int