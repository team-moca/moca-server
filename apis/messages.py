from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.extensions import db
from models import Message as MessageModel, schemas
import json

api = Namespace("messages", description="Message operations")

message_model = schemas.get_message_schema(api)

delete_model = api.model(
    "DeleteMessage",
    {
        "delete_everywhere": fields.Boolean(
            description="Delete the message for all contacts, if possible.",
            default=True,
        ),
    },
)


class Message(object):
    def __init__(self, message_id, contact_id, message, sent_datetime):
        self.message_id = message_id
        self.contact_id = contact_id
        self.message = message
        self.sent_datetime = sent_datetime


@api.route("/<string:chat_id>/messages")
class MessagesResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(message_model)
    @api.doc("list_messages")
    def get(self, chat_id, **kwargs):
        """List messages of a chat."""

        messages = (
            db.session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
        )
        return [
            Message(model.message_id, model.contact_id, json.loads(model.message), model.sent_datetime)
            for model in messages
        ]

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.expect(message_model)
    @api.doc("send_message")
    @api.response(204, "Message sent")
    def post(self, chat_id, **kwargs):
        """Send a message to a chat."""

        new_message = MessageModel(
            chat_id=chat_id,
            contact_id=api.payload.get("contact_id"),
            message=json.dumps(api.payload.get("message")),
        )
        db.session.add(new_message)
        db.session.commit()

        return "", 204


@api.route("/<string:chat_id>/messages/<string:message_id>")
class MessageResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.expect(message_model)
    @api.doc("edit_message")
    @api.response(204, "Message edited")
    def put(self, chat_id, message_id, **kwargs):
        """Edit a message."""
        message = (
            db.session.query(MessageModel)
            .filter(
                MessageModel.chat_id == chat_id, MessageModel.message_id == message_id
            )
            .first()
        )

        message.message = json.dumps(api.payload.message)

        db.session.commit()

        return "", 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("delete_message")
    @api.expect(delete_model)
    @api.response(204, "Message deleted")
    @api.response(
        403,
        "Message deletion failed because delete is disabled or nessage is too old to be deleted.",
    )
    def delete(self, chat_id, message_id, **kwargs):
        """Delete a message."""

        db.session.query(MessageModel).filter(
            MessageModel.chat_id == chat_id, MessageModel.message_id == message_id
        ).delete()
        db.session.commit()

        return "", 204


# @api.route('/<string:chat_id>/messages/<string:message_id>/pin')
# class MessageResource(Resource):

#     @auth.login_required
#     @api.doc(security=["jwt"])
#     @api.doc("pin_message")
#     @api.response(204, 'Message pinned')
#     def post(self, **kwargs):
#         """Pin a message."""
#         return '', 204

#     @auth.login_required
#     @api.doc(security=["jwt"])
#     @api.doc("unpin_message")
#     @api.response(204, 'Message unpinned')
#     def delete(self, **kwargs):
#         """Unpin a message."""
#         return '', 204
