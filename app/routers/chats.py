from datetime import datetime
from starlette.responses import Response
from app.models import Chat
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db
from fastapi.param_functions import Depends
from app.schemas import (
    ChatResponse,
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
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all chats the user has."""

    chats = crud.get_chats_for_user(db, current_user.user_id)

    if not chats:
        return []

    return sorted([
        ChatResponse(
            chat_id=chat.chat_id,
            user_id=chat.user_id,
            name=chat.name,
            is_muted=chat.is_muted,
            is_archived=chat.is_archived,
            pin_position=chat.pin_position,
            last_message=crud.get_last_message(db, current_user.user_id, chat.chat_id),
        )
        for chat in chats
    ], key=lambda chat: chat.last_message.sent_datetime if chat.last_message else datetime.min, reverse=True)


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
