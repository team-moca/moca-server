from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.version_helper import app_version
from core.extensions import db
from models import User, Contact, Chat, Message
import json

api = Namespace('debug', description="Debugging only methods")

# debug_model = api.model('ServerInfo', {
#     'version': fields.String(description="A semantic versioning number representing the current api version."),
#     'last_supported_version': fields.String(description="A semantic versioning number representing the last api version clients must have to connect to the server.")
# })

@api.route('/seed')
class SeedResource(Resource):
    @api.doc('seed')
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
            user_id=1
        )
        db.session.add(contact_jkahnwald)

        contact_mnielsen = Contact(
            service_id="DEMO",
            name="Martha Nielsen",
            username="mnielsen",
            phone="+492718281828"
        )
        db.session.add(contact_mnielsen)

        db.session.commit()

        # Create Chats

        new_chat = Chat(
            name="Windener Jugend",
            is_muted=False,
            is_archived=False,
            contacts=[contact_jkahnwald, contact_mnielsen]
        )
        db.session.add(new_chat)


        db.session.commit()

        # Create messages

        msg1 = Message(chat_id=new_chat.chat_id, contact_id=contact_jkahnwald.contact_id, message=json.dumps({ "type": "text", "content": "Hallo ihr alle! Ich bins, Jonas" }))
        msg2 = Message(chat_id=new_chat.chat_id, contact_id=contact_jkahnwald.contact_id, message=json.dumps({ "type": "text", "content": "Naa, was geht?" }))
        msg3 = Message(chat_id=new_chat.chat_id, contact_id=contact_mnielsen.contact_id, message=json.dumps({ "type": "text", "content": "Was wir wissen, ist ein Tropfen. Was wir nicht wissen, ist ein Ozean." }))

        db.session.add(msg1)
        db.session.add(msg2)
        db.session.add(msg3)

        db.session.commit()

        return {}
