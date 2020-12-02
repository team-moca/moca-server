import json

from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.error_codes import ErrorCode
from core.exceptions import NotFoundException
from core.extensions import db
from models import Chat as ChatModel
from apis.messages import Message
from models import Contact as ContactModel
from models import Message as MessageModel
import enum
from sqlalchemy.orm import joinedload
import itertools
from werkzeug.exceptions import NotFound

from models.schemas import get_contact_schema, get_chat_schema, ChatType

api = Namespace("contacts", description="Contact operations")

contact_model = get_contact_schema(api)

def getContactsForUser(user_id):
    return db.session.query(ContactModel).filter(ContactModel.user_id == user_id).all()

class Contact(object):
    def __init__(self, service_id, contact_id, name, username, phone, avatar, is_moca_user):
        self.service_id = service_id
        self.contact_id = contact_id
        self.name = name
        self.username = username
        self.phone = phone
        self.avatar = avatar
        self.is_moca_user = is_moca_user

@api.route("")
class ContactsResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(contact_model)
    @api.doc("list_contacts")
    def get(self, **kwargs):
        """Get a list of all chats the user has."""

        user_id = auth.current_user().get("payload", {}).get("user_id")
        contacts = (
            db.session.query(ContactModel)
            .filter(ContactModel.user_id == user_id)
            .all()
        )

        # early out if user has no associated contacts
        if len(contacts) == 0:
            return []

        return [
                    Contact(cm.service_id, cm.contact_id, cm.name, cm.username, cm.phone, cm.avatar, cm.is_moca_user)
                    for cm in contacts
                ]

@api.route("/<string:contact_id>")
class ContactResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(contact_model)
    @api.doc("get_contact")
    def get(self, contact_id, **kwargs):
        """Get a list of all chats the user has."""

        user_id = auth.current_user().get("payload", {}).get("user_id")
        cm = (
            db.session.query(ContactModel)
            .filter(ContactModel.user_id == user_id, ContactModel.contact_id == contact_id)
            .first()
        )

        if not cm:
            e = NotFound(f"Contact {contact_id} not found for user {user_id}.")
            e.data = {'code': ErrorCode.CONTACT_NOT_FOUND.name}
            raise e

        return Contact(cm.service_id, cm.contact_id, cm.name, cm.username, cm.phone, cm.avatar)


