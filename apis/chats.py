import json

from sqlalchemy import desc
from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.extensions import db
from core import connector
from models import Chat as ChatModel
from apis.messages import Message
from models import Contact as ContactModel
from models import Chat as ChatModel
from models import Message as MessageModel
import enum
from sqlalchemy.orm import joinedload
import itertools

from models.schemas import get_contact_schema, get_chat_schema, ChatType

api = Namespace("chats", description="Chat operations")

chat_model = get_chat_schema(api)


def getChatType(contacts):
    if len(contacts) == 2:
        # exactly two contacts (the user itself and one other)
        return ChatType.single
    if len(set([contact.user_id for contact in contacts])) == 1:
        # exactly two users (which could use multiple services)
        return ChatType.multi

    # otherwise, it's probably a group
    return ChatType.group


def getContactsForUser(user_id):
    return db.session.query(ContactModel).filter(ContactModel.user_id == user_id).all()




mute_model = api.model(
    "Mute",
    {
        "duration": fields.Integer(
            description="Duration in seconds. Omit to mute until manually unmuted.",
            min=0,
            example=28800,
        ),
        "allow_mentions": fields.Boolean(
            description="Bypasses mute if mentioned (e.g. @user hello...)", default=True
        ),
    },
)

pin_model = api.model(
    "Pin",
    {
        "position": fields.Integer(
            description="Position from top (0). Omit to automatically place the chat in the pinned section.",
            min=0,
        ),
    },
)

archive_model = api.model(
    "Archive",
    {
        "auto_unarchive": fields.Boolean(
            description="Auto unarchiving unarchives a chat when new messages arrive. Otherwise chats stay in the archive and don't send notifications.",
            default=True,
        ),
    },
)


class Contact(object):
    def __init__(self, service_id, contact_id, name, username, phone, avatar, is_moca_user):
        self.service_id = service_id
        self.contact_id = contact_id
        self.name = name
        self.username = username
        self.phone = phone
        self.avatar = avatar
        self.is_moca_user = is_moca_user


class Chat(object):
    def __init__(self, chat_id, chat_type, name, contacts, last_message):
        self.chat_id = chat_id
        self.chat_type = chat_type
        self.name = name
        self.contacts = contacts
        self.last_message = last_message


@api.route("")
class ChatsResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(chat_model)
    @api.doc("list_chats")
    def get(self, **kwargs):
        """Get a list of all chats the user has."""

        user_id = auth.current_user().get("payload", {}).get("user_id")

        chats = (
            db.session.query(ChatModel)
            .filter(ChatModel.user_id == user_id)
            .all()
        )

        return [
            Chat(
                model.chat_id,
                ChatType.unknown,
                model.name,
                None,
                get_last_message(model.chat_id)
            )
            for model in chats
        ]


def get_last_message(chat_id):
    model = (
        db.session.query(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(desc(MessageModel.sent_datetime)).first()
    )
    return Message(model.message_id, model.contact_id, json.loads(model.message), model.sent_datetime) if model else None



@api.route("/<string:chat_id>")
class ChatResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("delete_chat")
    @api.response(204, "Chat deleted")
    def delete(self, chat_id):
        """Delete a chat and all its messages. Cannot be undone."""

        db.session.query(ChatModel).filter(ChatModel.chat_id == chat_id).delete()
        db.session.commit()

        return "", 204


@api.route("/<string:chat_id>/mute")
class ChatMuteResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("mute")
    @api.expect(mute_model)
    @api.response(204, "Chat muted")
    def post(self, chat_id):
        """Mute a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.is_muted = True

        db.session.commit()

        return "", 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("unmute")
    @api.response(204, "Chat unmuted")
    def delete(self, chat_id):
        """Unmute a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.is_muted = False

        db.session.commit()

        return "", 204


@api.route("/<string:chat_id>/pin")
class ChatPinResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("pin")
    @api.expect(pin_model)
    @api.response(204, "Chat pinned")
    def post(self, chat_id):
        """Pin a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.pin_position = 0

        db.session.commit()

        return "", 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("unpin")
    @api.response(204, "Chat unpinned")
    def delete(self, chat_id):
        """Unpin a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.pin_position = None

        db.session.commit()

        return "", 204


@api.route("/<string:chat_id>/archive")
class ChatArchiveResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("archive")
    @api.expect(archive_model)
    @api.response(204, "Chat archived")
    def post(self, chat_id):
        """Archive a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.is_archived = False

        db.session.commit()

        return "", 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("unarchive")
    @api.response(204, "Chat unarchived")
    def delete(self, chat_id):
        """Unarchive a chat."""
        chat = (
            db.session.query(ChatModel)
            .filter(ChatModel.chat_id == chat_id, ChatModel.chat_id == chat_id)
            .first()
        )
        chat.is_archived = False

        db.session.commit()

        return "", 204
