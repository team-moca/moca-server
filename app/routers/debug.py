from app.database import Base
import json
from datetime import datetime
from app.models import Chat, Contact, Message, User
from app.dependencies import get_db, get_hashed_password
from fastapi import APIRouter
from fastapi import Depends
from setuptools_scm import get_version
from sqlalchemy.orm import Session
from app.schemas import Info

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/clear")
async def clear(db: Session = Depends(get_db)):
    """Clears the database."""

    Base.metadata.drop_all()
    Base.metadata.create_all()

    return {}


@router.post("/seed")
async def seed(db: Session = Depends(get_db)):
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

    # Create Contacts

    contact_jkahnwald = Contact(
        service_id="DEMO",
        name="Jonas Kahnwald",
        username="jkahnwald",
        phone="+49314159265",
        avatar="https://i.pravatar.cc/150?u=2",
        user_id=1,
        is_moca_user=True,
    )
    db.add(contact_jkahnwald)

    contact_mnielsen = Contact(
        service_id="DEMO",
        name="Martha Nielsen",
        username="mnielsen",
        phone="+492718281828",
        avatar="https://i.pravatar.cc/150?u=4",
        user_id=1,
    )
    db.add(contact_mnielsen)

    db.commit()

    # Create Chats

    new_chat = Chat(
        user_id=1,
        name="Windener Jugend",
        is_muted=False,
        is_archived=False,
        contacts=[contact_jkahnwald, contact_mnielsen],
    )
    db.add(new_chat)

    db.commit()

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
