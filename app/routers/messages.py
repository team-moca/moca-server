import uuid
from datetime import datetime
from app.pool import Pool
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
from app.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_db,
    get_pagination,
    get_pool,
)
from fastapi.param_functions import Depends
from app.schemas import (
    ChatResponse,
    DeleteMessageRequest,
    Message,
    MessageContent,
    MessageResponse,
    Pagination,
    Pin,
    RegisterRequest,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])

def prepare_message(chat_id, message_id, message):
    msg = json.loads(message)
    if 'url' in msg:
        msg["url"] = f"/chats/{chat_id}/messages/{message_id}/media"
    return msg

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

    messages = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .order_by(desc_op(models.Message.sent_datetime))
        .limit(pagination.count)
        .offset(pagination.page * pagination.count)
        .all()
    )

    if not messages:
        return []

    return [
        MessageResponse(
            message_id=message.message_id,
            contact_id=message.contact_id,
            sent_datetime=message.sent_datetime,
            message=prepare_message(chat.chat_id, message.message_id, message.message),
        )
        for message in messages
    ]


@router.post("", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message: Message,
    pool: Pool = Depends(get_pool),
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Send a message to a chat."""
    chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    connector_id = chat.contacts[0].contact.connector_id
    connector = crud.get_connector(db, current_user.user_id, connector_id)

    if connector.connector_type == "DEMO":
        new_message = models.Message(
            chat_id=chat_id,
            contact_id=connector.connector_user_id,
            message=json.dumps(message.message.__dict__),
            sent_datetime=datetime.now(),
        )
        db.add(new_message) # add is ok here
        db.commit()

    else:
        sent = await pool.get(
            f"{connector.connector_type}/{connector.connector_id}/{str(uuid.uuid4())}/send_message",
            {"chat_id": chat.internal_id, "message": message.message.__dict__},
        )

        # This should never be null
        contact = db.query(models.Contact).filter(models.Contact.connector_id == connector_id).first()

        new_message = models.Message(
            crud.get_id(connector.connector_id, sent.get("message_id")),
            internal_id=sent.get("message_id"),
            chat_id=chat_id,
            contact_id=contact.contact_id,
            message=json.dumps(message.message.__dict__),
            sent_datetime=datetime.now(),
        )
        db.merge(new_message)
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
    """Delete a message.
    Not all services support message deletion."""
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
    """Edit a message.
    Not all services support message editing."""
    edit_message = (
        db.query(models.Message)
        .filter(
            models.Message.chat_id == chat_id, models.Message.message_id == message_id
        )
        .first()
    )

    edit_message.message = json.dumps(message.__dict__)
    db.commit()


@router.get("/{message_id}/media", response_class=Response)
async def download_media(
    chat_id: int,
    message_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    pool: Pool = Depends(get_pool),
    db: Session = Depends(get_db),
):
    """Download a media file.
    Not all messages have a media file attached to it."""
    chat = crud.get_chat(db, current_user.user_id, chat_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The chat with id {chat_id} does not exist.",
        )

    connector_id = chat.contacts[0].contact.connector_id
    connector = crud.get_connector(db, current_user.user_id, connector_id)

    message = db.query(models.Message).filter(models.Message.message_id == message_id).first()

    filename, mime, data = await pool.get_bytes(
        f"{connector.connector_type}/{connector_id}/{uuid.uuid4()}/chats/{chat.internal_id}/messages/{message.internal_id}/get_media", {}
    )

    if data:

        return Response(data, media_type=mime)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"File {filename} does not exist.",
    )
