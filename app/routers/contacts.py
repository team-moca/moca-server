from starlette.responses import Response
from app.models import Contact
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db
from fastapi.param_functions import Depends
from app.schemas import (
    ContactResponse,
    Pin,
    RegisterRequest,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactResponse])
async def get_contacts(
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all contacts the user has."""

    contacts = crud.get_contacts_for_user(db, current_user.user_id)

    if not contacts:
        return []

    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    return crud.get_contact(db, current_user.user_id, contact_id)
