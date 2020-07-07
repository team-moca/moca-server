from flask import Flask
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app,
        title="MOCA Server API",
        version="0.1.0",
        description="REST API reference for mobile and web clients connecting to MOCA Server."
        )

chats = api.namespace('chats', description='chats operations')

contact_model = api.model('Contact', {
    'service_id': fields.String,
    'contact_id': fields.String,
    'name': fields.String
})

chat_model = api.model('Chat', {
    'chat_id': fields.String,
    'name': fields.String,
    'contacts': fields.List(fields.Nested(contact_model))
})

mute_model = api.model('Mute', {
    'duration': fields.Integer(description="Duration in seconds. Omit to mute until manually unmuted.", min=0, example=28800),
    'allow_mentions': fields.Boolean(description="Bypasses mute if mentioned (e.g. @user hello...)", default=True)    
})

pin_model = api.model('Pin', {
    'position': fields.Integer(description="Position from top (0). Omit to automatically place the chat in the pinned section.", min=0),
})

class Contact(object):
    def __init__(self, service_id, contact_id, name):
        self.service_id = service_id
        self.contact_id = contact_id
        self.name = name

class Chat(object):
    def __init__(self, chat_id, name, contacts):
        self.chat_id = chat_id
        self.name = name
        self.contacts = contacts

@chats.route('/')
class ChatsResource(Resource):
    @chats.marshal_list_with(chat_model)
    @chats.doc("list_chats")
    def get(self, **kwargs):
        """Get a list of all chats the user has."""
        return [
            Chat('CHAT0', "Chat Zero", [Contact("TELEGRAM", "HGTannhaus", "H. G. Tannhaus")]),
            Chat("CHAT1", "Chat One (Group Chat)", [Contact("WHATSAPP", "JKahnwald", "Jonas Kahnwald"), Contact("WHATSAPP", "MNielsen", "Martha Nielsen")])
        ]

@chats.route('/<string:id>')
class ChatResource(Resource):
    @chats.doc('delete_chat')
    @chats.response(204, 'Chat deleted')
    def delete(self, id):
        '''Delete a chat and all its messages. Cannot be undone.'''
        return '', 204

@chats.route('/<string:id>/mute')
class ChatMuteResource(Resource):
    @chats.doc('mute')
    @chats.expect(mute_model)
    @chats.response(204, 'Chat muted')
    def post(self, id):
        '''Mute a chat.'''
        return '', 204

    @chats.doc('unmute')
    @chats.response(204, 'Chat unmuted')
    def delete(self, id):
        '''Unmute a chat.'''
        return '', 204

@chats.route('/<string:id>/pin')
class ChatPinResource(Resource):
    @chats.doc('pin')
    @chats.expect(pin_model)
    @chats.response(204, 'Chat pinned')
    def post(self, id):
        '''Pin a chat.'''
        return '', 204

    @chats.doc('unpin')
    @chats.response(204, 'Chat unpinned')
    def delete(self, id):
        '''Unpin a chat.'''
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)