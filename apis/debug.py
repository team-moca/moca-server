from datetime import datetime

from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.version_helper import app_version
from core.extensions import db, mqtt
from models import User, Contact, Chat, Message
import json

api = Namespace("debug", description="Debugging only methods")

# debug_model = api.model('ServerInfo', {
#     'version': fields.String(description="A semantic versioning number representing the current api version."),
#     'last_supported_version': fields.String(description="A semantic versioning number representing the last api version clients must have to connect to the server.")
# })


@api.route("/database/seed")
class SeedResource(Resource):
    @api.doc("seed")
    def post(self):
        """Clear the database and seed it with demo data."""

        db.drop_all()
        db.create_all()

        # Create Users

        new_user = User(
            username="jkahnwald",
            mail="jkahnwald@stadt-winden.de",
            password_hash="53fab271885be6d753d501940409376b94ca7b7a",
            is_verified=True,
        )
        db.session.add(new_user)

        # Create Contacts

        contact_jkahnwald = Contact(
            service_id="DEMO",
            name="Jonas Kahnwald",
            username="jkahnwald",
            phone="+49314159265",
            avatar="https://i.pravatar.cc/150?u=2",
            user_id=1,
            is_moca_user=True
        )
        db.session.add(contact_jkahnwald)

        contact_mnielsen = Contact(
            service_id="DEMO",
            name="Martha Nielsen",
            username="mnielsen",
            phone="+492718281828",
            avatar="https://i.pravatar.cc/150?u=4",
            user_id=1
        )
        db.session.add(contact_mnielsen)

        db.session.commit()

        # Create Chats

        new_chat = Chat(
            name="Windener Jugend",
            is_muted=False,
            is_archived=False,
            contacts=[contact_jkahnwald, contact_mnielsen],
        )
        db.session.add(new_chat)

        db.session.commit()

        # Create messages

        msg1 = Message(
            chat_id=new_chat.chat_id,
            contact_id=contact_jkahnwald.contact_id,
            message=json.dumps(
                {"type": "text", "content": "Hallo ihr alle! Ich bins, Jonas"}
            ),
            sent_datetime=datetime(2020, 11, 11, 9, 2, 30)
        )
        msg2 = Message(
            chat_id=new_chat.chat_id,
            contact_id=contact_jkahnwald.contact_id,
            message=json.dumps({"type": "text", "content": "Naa, was geht?"}),
            sent_datetime=datetime(2020, 11, 11, 9, 3, 24)
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
            sent_datetime=datetime(2020, 11, 11, 9, 5, 12)
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
            sent_datetime=datetime(2020, 11, 11, 9, 12, 59)
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
            sent_datetime=datetime(2020, 11, 11, 9, 14, 37)
        )

        db.session.add(msg1)
        db.session.add(msg2)
        db.session.add(msg3)
        db.session.add(msg4)
        db.session.add(msg5)

        db.session.commit()

        return {}


@api.route("/database/clear")
class SeedResource(Resource):
    @api.doc("clear")
    def post(self):
        """Clear the database."""

        db.drop_all()
        db.create_all()

        mqtt.publish("debug/database", json.dumps({"event": "clear"}))

        return {}
