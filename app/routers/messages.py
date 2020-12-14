import json
from sqlalchemy.sql.operators import desc_op
from starlette.responses import Response
from app import models
from app.models import Chat
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db, get_pagination
from fastapi.param_functions import Depends
from app.schemas import (
    ChatResponse,
    DeleteMessageRequest,
    Message,
    MessageContent,
    MessageResponse, Pagination,
    Pin,
    RegisterRequest,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])


@router.get("", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int,
    pagination: Pagination = Depends(get_pagination),
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all messages for a specific chat."""

    chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    messages = db.query(models.Message).filter(models.Message.chat_id == chat_id).order_by(desc_op(models.Message.sent_datetime)).limit(pagination.count).offset(pagination.page * pagination.count).all()

    if not messages:
        return []

    return [
        MessageResponse(
            message_id=message.message_id,
            contact_id=message.contact_id,
            sent_datetime=message.sent_datetime,
            message=json.loads(message.message),
        )
        for message in messages
    ]


@router.post("", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message: Message,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    new_message = models.Message(
        chat_id=chat_id,
        contact_id=message.contact_id,
        message=json.dumps(message.message),
        sent_datetime=message.sent_datetime,
    )
    db.add(new_message)
    db.commit()

    return MessageResponse(
        message_id=new_message.message_id,
        contact_id=new_message.contact_id,
        sent_datetime=new_message.sent_datetime,
        message=json.loads(new_message.message),
    )


@router.delete(
    "/{message_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_message(
    chat_id: int,
    message_id: int,
    request: DeleteMessageRequest,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    db.query(models.Message).filter(
        models.Message.chat_id == chat_id, models.Message.message_id == message_id
    ).delete()
    db.commit()


@router.put(
    "/{message_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def edit_message(
    chat_id: int,
    message_id: int,
    message: MessageContent,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    edit_message = (
        db.query(models.Message)
        .filter(
            models.Message.chat_id == chat_id, models.Message.message_id == message_id
        )
        .first()
    )

    edit_message.message = json.dumps(message.__dict__)
    db.commit()
