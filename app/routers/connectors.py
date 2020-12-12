from starlette.responses import Response
from app import models
from app.models import Connector
from typing import List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db
from fastapi.param_functions import Depends
from app.schemas import (
    ConnectorResponse,
    Pin,
    RegisterRequest,
    User,
    UserResponse,
    VerifyRequest,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("", response_model=List[ConnectorResponse])
async def get_connectors(
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Get a list of all connectors the user has."""

    connectors = db.query(models.Connector).filter(models.Connector.user_id == current_user.user_id).all()

    if not connectors:
        return []

    return connectors


@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    connector = db.query(models.Connector).filter(models.Connector.user_id == current_user.user_id, models.Connector.connector_id == connector_id).first()

    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector {connector_id} not found.",
        )

    return connector
