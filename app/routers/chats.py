from datetime import datetime
import json
from os import name
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.operators import desc_op
from starlette.responses import Response
from app import models
from app import schemas
from app.models import Chat
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session, joinedload
from app.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_db,
    get_pagination,
)
from fastapi.param_functions import Depends
from app.schemas import (
    ChatDetailsResponse,
    ChatResponse,
    ContactResponse,
    Pagination,
    Pin,
    RegisterRequest,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=List[ChatResponse])
async def get_chats(
    pagination: Pagination = Depends(get_pagination),
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all chats the user has."""

    chats_with_message = (
        db.query(
            models.Chat,
            models.Connector,
            models.Message,
            func.max(models.Message.sent_datetime),
        )
        .join(models.Connector)
        .join(models.Message)
        .group_by(models.Message.chat_id)
        .filter(models.Connector.user_id == current_user.user_id)
        .order_by(desc_op(models.Message.sent_datetime))
        .limit(pagination.count)
        .offset(pagination.page * pagination.count)
        .all()
    )

    if not chats_with_message:
        return []

    return [
        ChatResponse(
            chat_id=chat_with_message[0].chat_id,
            connector_id=chat_with_message[0].connector_id,
            name=chat_with_message[0].name,
            is_muted=chat_with_message[0].is_muted,
            is_archived=chat_with_message[0].is_archived,
            pin_position=chat_with_message[0].pin_position,
            last_message=schemas.MessageResponse(
                message_id=chat_with_message[2].message_id,
                contact_id=chat_with_message[2].contact_id,
                message=json.loads(chat_with_message[2].message),
                sent_datetime=chat_with_message[2].sent_datetime,
            )
            if chat_with_message[2]
            else None,
        )
        for chat_with_message in chats_with_message
    ]

@router.get("/{chat_id}", response_model=ChatDetailsResponse)
async def get_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a detailed chat object. Contains information about the participants of the chat."""

    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    contacts = []

    for rel in chat.contacts:

        contact = crud.get_contact(db, current_user.user_id, rel.contact_id)
        contacts.append(ContactResponse(
            contact_id=contact.contact_id,
            connector_id=contact.connector_id,
            name=contact.name,
            is_self=contact.is_self,
            service_id=contact.service_id
        ))

    return ChatDetailsResponse(
        chat_id=chat_id,
        connector_id=chat.connector_id,
        name=chat.name,
        is_muted=chat.is_muted,
        is_archived=chat.is_archived,
        pin_position=chat.pin_position,
        participants=contacts
    )



@router.delete(
    "/{chat_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Deletes a chat and all its messages. This action cannot be undone."""

    db.query(Chat).filter(Chat.chat_id == chat_id).delete()
    db.commit()


@router.post(
    "/{chat_id}/mute", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def mute_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Mute a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.is_muted = True
    db.commit()


@router.delete(
    "/{chat_id}/mute", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def unmute_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Unmute a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.is_muted = False
    db.commit()


@router.post(
    "/{chat_id}/archive",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def archive_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Archive a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.is_archived = True
    db.commit()


@router.delete(
    "/{chat_id}/archive",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def unarchive_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Unarchive a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.is_archived = False
    db.commit()


@router.put(
    "/{chat_id}/pin", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def pin_chat(
    chat_id: int,
    pin: Pin,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Pin a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.pin_position = pin.pin_position
    db.commit()


@router.delete(
    "/{chat_id}/pin", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def unpin_chat(
    chat_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Unpin a chat."""

    chat: Chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    chat.pin_position = None
    db.commit()
