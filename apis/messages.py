from flask_restx import Namespace, Resource, fields
from core.auth import auth

api = Namespace('messages', description='Message operations')

message_model = api.model('Message', {
    "from_user_id": fields.Integer(description="Sender's user id", example=100),
    "to_user_id": fields.Integer(description="Receipient's user id", example=200),
    "service_id": fields.String(description="ID of the service this message has been / should be sent with", example="TELEGRAM"),
    "message_type": fields.String(description="Type of message.", example="text"),
    "message": fields.Raw(description="A JSON object representing the message. The object schema is based on the message type.")
})

class Message(object):
    def __init__(self, from_user_id, to_user_id, service_id, message_type, message):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.service_id = service_id
        self.message_type = message_type
        self.message = message

@api.route('/<string:chat_id>/messages')
class MessagesResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(message_model)
    @api.doc("list_messages")
    def get(self, **kwargs):
        """List messages of a chat."""
        return [
            Message(100, 200, "TELEGRAM", "text", {"content": "Hello two hundred, how are you?"}),
            Message(200, 100, "TELEGRAM", "text", {"content": "I'm fine, thank you!"})
        ]

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.expect(message_model)
    @api.doc("send_message")
    @api.response(204, 'Message sent')
    def post(self, **kwargs):
        """Send a message to a chat."""
        return '', 204

@api.route('/<string:chat_id>/messages/<string:message_id>')
class MessageResource(Resource):

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.expect(message_model)
    @api.doc("edit_message")
    @api.response(204, 'Message edited')
    def put(self, **kwargs):
        """Edit a message."""
        return '', 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("delete_message")
    @api.response(204, 'Message deleted')
    @api.response(403, 'Message deletion failed because delete is disabled or nessage is too old to be deleted.')
    def delete(self, **kwargs):
        """Delete a message."""
        return '', 204

@api.route('/<string:chat_id>/messages/<string:message_id>/pin')
class MessageResource(Resource):

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(message_model)
    @api.doc("list_pinned_messages")
    def get(self, **kwargs):
        """List pinned message(s). Depending on the service implementation, the list might contain multiple, one or no messages."""
        return [
            Message(100, 200, "TELEGRAM", "text", {"content": "Hi, I'm a pinned message."}),
        ]

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("pin_message")
    @api.response(204, 'Message pinned')
    def post(self, **kwargs):
        """Pin a message."""
        return '', 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("unpin_message")
    @api.response(204, 'Message unpinned')
    def delete(self, **kwargs):
        """Unpin a message."""
        return '', 204
