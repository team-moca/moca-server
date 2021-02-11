import uuid
import json
from app.pool import Pool
from starlette.responses import Response
from app import models
from app.models import Connector
from typing import Dict, List
from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_db,
    get_pool,
)
from fastapi.param_functions import Depends
from app.schemas import (
    ConnectorResponse,
    InitializeConnectorRequest,
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

    connectors = (
        db.query(models.Connector)
        .filter(models.Connector.user_id == current_user.user_id)
        .all()
    )

    if not connectors:
        return []

    return connectors


@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    return crud.get_connector(db, current_user.user_id, connector_id)


@router.post("", response_model=ConnectorResponse)
async def initialize_connector(
    request: InitializeConnectorRequest,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    pool: Pool = Depends(get_pool),
):
    """Get a connector id to start configuring a connector (via PUT /connectors/{connector_id})."""

    new_connector = Connector(
        connector_type=request.connector_type,
        user_id=current_user.user_id,
    )
    db.add(new_connector)
    db.commit()

    return new_connector


@router.put("/{connector_id}")
async def setup_connector(
    connector_id: int,
    request: Dict,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    pool: Pool = Depends(get_pool),
):
    """Configure a connector."""

    connector = crud.get_connector(db, current_user.user_id, connector_id)

    response = await pool.get(
        f"{connector.connector_type}/{connector_id}/{str(uuid.uuid4())}/configure",
        request,
    )

    if response.get("step") == "finished":
        contact = response.get("data", {}).get("contact")

        # 2. Create contact if not already exists

        if (
            db.query(models.Contact)
            .filter(models.Contact.internal_id == contact.get("contact_id"), models.Contact.connector_id == connector_id)
            .count()
            == 0
        ):
            new_contact = models.Contact(
                internal_id=contact.get("contact_id"),
                service_id=connector.connector_type,
                name=contact.get("name"),
                username=contact.get("username"),
                phone=contact.get("phone"),
                connector_id=connector.connector_id,
                is_self=True,
            )
            db.add(new_contact)

        # 3. Create connector
        connector.connector_user_id = contact.get("contact_id")
        db.commit()

    return response


@router.delete(
    "/{connector_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_connector(
    connector_id: int,
    current_user: UserResponse = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    pool: Pool = Depends(get_pool),
):
    """Delete a connector."""

    connector = crud.get_connector(db, current_user.user_id, connector_id)

    response = await pool.get(
        f"{connector.connector_type}/{connector_id}/{str(uuid.uuid4())}/delete_connector",
        {},
    )

    if response.get("success"):
        db.query(models.Connector).filter(
            models.Connector.connector_id == connector_id
        ).delete()
        db.commit()

    # else:
    #     print("ERROR DELETING CONNECTOR")
