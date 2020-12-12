import random
from datetime import datetime
from typing import List
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from fastapi import status
from . import models, schemas
from .dependencies import get_hashed_password
import logging

_LOGGER = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.RegisterRequest):
    hashed_password = get_hashed_password(user.password)

    verification_code = "{:06d}".format(random.randint(0, 999999))

    print(f"Verification code for user {user.username}: {verification_code}")

    db_user = models.User(
        username = user.username,
        mail = user.mail,
        hashed_password = hashed_password,
        is_verified = False,
        verification_code = verification_code,
        created_at = datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def verify_user(db: Session, request: schemas.VerifyRequest):
    user = get_user_by_username(db, request.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {request.username} does not exist.",
        )

    if not user.verification_code == request.verification_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Verification code wrong."
        )

    user.is_verified = True
    db.commit()

    return user

def get_chats_for_user(db: Session, user_id: int) -> List[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.user_id == user_id).all()

def get_chat(db: Session, user_id: int, chat_id: int) -> models.Chat:
    return db.query(models.Chat).filter(models.Chat.user_id == user_id, models.Chat.chat_id == chat_id).first()
