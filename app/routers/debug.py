from app import models
from app.database import Base
import json
from datetime import datetime, timedelta
from app.models import Chat, Contact, Message, User, Connector, Session as SessionModel
from app.dependencies import get_db, get_hashed_password
from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from setuptools_scm import get_version
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

USERNAME = os.getenv("MOCA_DEBUG_USERNAME")
PASSWORD = os.getenv("MOCA_DEBUG_PASSWORD")

security = HTTPBasic()


router = APIRouter(prefix="/debug", tags=["debug"])

def debug_login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.post("/clear")
async def clear(db: Session = Depends(get_db), username: str = Depends(debug_login)):
    """Clears the database."""

    Base.metadata.drop_all()
    Base.metadata.create_all()

    return {}


@router.post("/seed")
async def seed(db: Session = Depends(get_db), username: str = Depends(debug_login)):
    """Clears the database and fills it with demo data."""

    Base.metadata.drop_all()
    Base.metadata.create_all()

    # Create Users

    new_user = User(
        username="jkahnwald",
        mail="jkahnwald@stadt-winden.de",
        hashed_password=get_hashed_password("jkahnwald"),
        is_verified=True,
    )
    db.add(new_user)

    new_user = User(
        username="tomschneider",
        mail="tomschneider@stadt-winden.de",
        hashed_password=get_hashed_password("tomschneider"),
        is_verified=True,
    )
    db.add(new_user)

    new_user = User(
        username="nickschestag",
        mail="nickschestag@stadt-winden.de",
        hashed_password=get_hashed_password("nickschestag"),
        is_verified=True,
    )
    db.add(new_user)

    # Create new login session
    new_session = SessionModel(
        user_id=1,
        name="iPhone von Jonas",
        valid_until=datetime.now() + timedelta(days=30),
    )
    db.add(new_session)

    # Create Demo connector

    new_connector = Connector(connector_type="DEMO", user_id=1, connector_user_id="1")
    db.add(new_connector)
    db.commit()

    # Create Contacts

    contact_jkahnwald = Contact(
        service_id="DEMO",
        name="Jonas Kahnwald",
        username="jkahnwald",
        phone="+49314159265",
        avatar="https://i.pravatar.cc/150?u=2",
        connector_id=new_connector.connector_id,
        is_self=True,
    )
    db.add(contact_jkahnwald)

    contact_mnielsen = Contact(
        service_id="DEMO",
        name="Martha Nielsen",
        username="mnielsen",
        phone="+492718281828",
        avatar="https://i.pravatar.cc/150?u=4",
        connector_id=new_connector.connector_id,
    )
    db.add(contact_mnielsen)

    db.commit()

    # Create Chats

    new_chat = Chat(
        connector_id=new_connector.connector_id,
        name="Windener Jugend",
        is_muted=False,
        is_archived=False,
    )
    db.add(new_chat)

    db.commit()

    db.add(
        models.ContactsChatsRelationship(
            contact_id=contact_jkahnwald.contact_id, chat_id=new_chat.chat_id
        )
    )
    db.add(
        models.ContactsChatsRelationship(
            contact_id=contact_mnielsen.contact_id, chat_id=new_chat.chat_id
        )
    )

    # Create messages

    msg1 = Message(
        chat_id=new_chat.chat_id,
        contact_id=contact_jkahnwald.contact_id,
        message=json.dumps(
            {"type": "text", "content": "Hallo ihr alle! Ich bins, Jonas"}
        ),
        sent_datetime=datetime(2020, 11, 11, 9, 2, 30),
    )
    msg2 = Message(
        chat_id=new_chat.chat_id,
        contact_id=contact_jkahnwald.contact_id,
        message=json.dumps({"type": "text", "content": "Naa, was geht?"}),
        sent_datetime=datetime(2020, 11, 11, 9, 3, 24),
    )
    msg3 = Message(
        chat_id=new_chat.chat_id,
        contact_id=contact_mnielsen.contact_id,
        message=json.dumps(
            {
                "type": "text",
                "content": "Was wir wissen, ist ein Tropfen. Was wir nicht wissen, ist ein Ozean.",
            }
        ),
        sent_datetime=datetime(2020, 11, 11, 9, 5, 12),
    )

    msg4 = Message(
        chat_id=new_chat.chat_id,
        contact_id=contact_mnielsen.contact_id,
        message=json.dumps(
            {
                "type": "image",
                "url": "https://img.posterlounge.de/images/l/1891341.jpg",
            }
        ),
        sent_datetime=datetime(2020, 11, 11, 9, 12, 59),
    )

    msg5 = Message(
        chat_id=new_chat.chat_id,
        contact_id=contact_mnielsen.contact_id,
        message=json.dumps(
            {
                "type": "video",
                "url": "https://bit.ly/2KAZmtK",
            }
        ),
        sent_datetime=datetime(2020, 11, 11, 9, 14, 37),
    )

    db.add(msg1)
    db.add(msg2)
    db.add(msg3)
    db.add(msg4)
    db.add(msg5)

    db.commit()

    return {}
