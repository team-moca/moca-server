from flask_restx import Namespace, Resource, fields
from core.auth import auth
import enum

api = Namespace('chats', description='Chat operations')

contact_model = api.model('Contact', {
    'service_id': fields.String,
    'contact_id': fields.String,
    'name': fields.String
})

class ChatType(enum.Enum):
    single = 'single'
    multi = 'multi'
    group = 'group'

chat_model = api.model('Chat', {
    'chat_id': fields.String,
    'name': fields.String,
    'chat_type': fields.String(description="Type of chat. single for a normal one to one chat, multi for a chat that combines the chat with one person via multiple services, group for groups (via exactly one service).", example="single", enum=ChatType._member_names_),
    'contacts': fields.List(fields.Nested(contact_model))
})

mute_model = api.model('Mute', {
    'duration': fields.Integer(description="Duration in seconds. Omit to mute until manually unmuted.", min=0, example=28800),
    'allow_mentions': fields.Boolean(description="Bypasses mute if mentioned (e.g. @user hello...)", default=True)    
})

pin_model = api.model('Pin', {
    'position': fields.Integer(description="Position from top (0). Omit to automatically place the chat in the pinned section.", min=0),
})

archive_model = api.model('Archive', {
    'auto_unarchive': fields.Boolean(description="Auto unarchiving unarchives a chat when new messages arrive. Otherwise chats stay in the archive and don't send notifications.", default=True),
})

class Contact(object):
    def __init__(self, service_id, contact_id, name):
        self.service_id = service_id
        self.contact_id = contact_id
        self.name = name

class Chat(object):
    def __init__(self, chat_id, chat_type, name, contacts):
        self.chat_id = chat_id
        self.chat_type = chat_type
        self.name = name
        self.contacts = contacts

@api.route('')
class ChatsResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.marshal_list_with(chat_model)
    @api.doc("list_chats")
    def get(self, **kwargs):
        """Get a list of all chats the user has."""
        return [
            Chat('CHAT0', ChatType.single, "Chat Zero", [Contact("TELEGRAM", "HGTannhaus", "H. G. Tannhaus")]),
            Chat("CHAT1", ChatType.group, "Chat One (Multi Chat)", [Contact("WHATSAPP", "silja_wa", "Silja"), Contact("TELEGRAM", "silja_tg", "Silja")]),
            Chat("CHAT2", ChatType.group, "Chat Two (Group Chat)", [Contact("WHATSAPP", "JKahnwald", "Jonas Kahnwald"), Contact("WHATSAPP", "MNielsen", "Martha Nielsen")])
        ]

@api.route('/<string:id>')
class ChatResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('delete_chat')
    @api.response(204, 'Chat deleted')
    def delete(self, id):
        '''Delete a chat and all its messages. Cannot be undone.'''
        return '', 204

@api.route('/<string:id>/mute')
class ChatMuteResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('mute')
    @api.expect(mute_model)
    @api.response(204, 'Chat muted')
    def post(self, id):
        '''Mute a chat.'''
        return '', 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('unmute')
    @api.response(204, 'Chat unmuted')
    def delete(self, id):
        '''Unmute a chat.'''
        return '', 204

@api.route('/<string:id>/pin')
class ChatPinResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('pin')
    @api.expect(pin_model)
    @api.response(204, 'Chat pinned')
    def post(self, id):
        '''Pin a chat.'''
        return '', 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('unpin')
    @api.response(204, 'Chat unpinned')
    def delete(self, id):
        '''Unpin a chat.'''
        return '', 204

@api.route('/<string:id>/archive')
class ChatArchiveResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('archive')
    @api.expect(archive_model)
    @api.response(204, 'Chat archived')
    def post(self, id):
        '''Archive a chat.'''
        return '', 204

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc('unarchive')
    @api.response(204, 'Chat unarchived')
    def delete(self, id):
        '''Unarchive a chat.'''
        return '', 204
