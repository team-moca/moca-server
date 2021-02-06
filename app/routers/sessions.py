from datetime import datetime
from starlette.responses import Response
from app import models
from app.models import Chat
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db
from fastapi.param_functions import Depends
from app.schemas import (
    AuthUser,
    ChatResponse,
    Pin,
    RegisterRequest,
    SessionResponse,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/sessions", tags=["sessions"])

SESSION_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Session not found.",
)


@router.get("", response_model=List[SessionResponse])
async def get_sessions(
    current_user: AuthUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all active sessions the user has."""

    sessions = (
        db.query(models.Session)
        .filter(
            models.Session.user_id == current_user.user_id,
            models.Session.valid_until > datetime.now(),
        )
        .all()
    )

    if not sessions:
        return []

    return sessions


@router.get("/current", response_model=SessionResponse)
async def get_session(
    current_user: AuthUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get the current session."""

    session = (
        db.query(models.Session)
        .filter(
            models.Session.user_id == current_user.user_id,
            models.Session.session_id == current_user.session_id,
            models.Session.valid_until > datetime.now(),
        )
        .first()
    )

    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: AuthUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get the current session."""

    session = (
        db.query(models.Session)
        .filter(
            models.Session.session_id == session_id,
            models.Session.valid_until > datetime.now(),
        )
        .first()
    )

    if not session:
        raise SESSION_NOT_FOUND

    return session


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_all_but_this_session(
    current_user: AuthUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Logout from all sessions (except the current one)."""

    db.query(models.Session).filter(
        models.Session.user_id == current_user.user_id,
        models.Session.session_id != current_user.session_id,
    ).delete()
    db.commit()


@router.delete(
    "/{session_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_session(
    session_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Logout from one session."""

    db.query(models.Session).filter(
        models.Session.user_id == current_user.user_id,
        models.Session.session_id == session_id,
    ).delete()
    db.commit()
