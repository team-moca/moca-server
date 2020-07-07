from flask import Flask, request
from flask_restx import Api, Resource, fields
from werkzeug.security import safe_str_cmp
from functools import wraps
from flask_httpauth import HTTPTokenAuth

authorization = HTTPTokenAuth(scheme='Bearer')

tokens = {
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImprYWhud2FsZCIsImlhdCI6MTUxNjIzOTAyMn0.meNzV4ABOhmN_CxmzBkzTH1m4gpdEv3vrJBl89dllgY': 'jkahnwald'
}

@authorization.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

@authorization.error_handler
def authorization_error(status):
    return {'message': 'Unauthorized'}, status

app = Flask(__name__)

authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(app,
        title="MOCA Server API",
        version="0.1.0",
        description="REST API reference for mobile and web clients connecting to MOCA Server.",
        authorizations=authorizations,
        security=[]
        )

chats = api.namespace('chats', description='Chat operations')
auth = api.namespace('auth', description="Authentication")

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

credentials_model = api.model('Credentials',{
    'username': fields.String(example="jkahnwald"),
    'hash': fields.String(description="The hash can be calculated like this: sha1(username + password). Username and password must be utf-8 encoded.")
})

token_model = api.model('Token', {
    'token': fields.String(description="A JWT token that can be used to access restricted resources.")
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

@api.route('/test')
class Test(Resource):
    @authorization.login_required
    @api.doc(security=["jwt"])
    def get(self):
        return {'hello': f'{authorization.current_user()}'}

@chats.route('/')
class ChatsResource(Resource):
    @authorization.login_required
    @chats.doc(security=["jwt"])
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
    @authorization.login_required
    @chats.doc(security=["jwt"])
    @chats.doc('delete_chat')
    @chats.response(204, 'Chat deleted')
    def delete(self, id):
        '''Delete a chat and all its messages. Cannot be undone.'''
        return '', 204

@chats.route('/<string:id>/mute')
class ChatMuteResource(Resource):
    @authorization.login_required
    @chats.doc(security=["jwt"])
    @chats.doc('mute')
    @chats.expect(mute_model)
    @chats.response(204, 'Chat muted')
    def post(self, id):
        '''Mute a chat.'''
        return '', 204

    @authorization.login_required
    @chats.doc(security=["jwt"])
    @chats.doc('unmute')
    @chats.response(204, 'Chat unmuted')
    def delete(self, id):
        '''Unmute a chat.'''
        return '', 204

@chats.route('/<string:id>/pin')
class ChatPinResource(Resource):
    @authorization.login_required
    @chats.doc(security=["jwt"])
    @chats.doc('pin')
    @chats.expect(pin_model)
    @chats.response(204, 'Chat pinned')
    def post(self, id):
        '''Pin a chat.'''
        return '', 204

    @authorization.login_required
    @chats.doc(security=["jwt"])
    @chats.doc('unpin')
    @chats.response(204, 'Chat unpinned')
    def delete(self, id):
        '''Unpin a chat.'''
        return '', 204

@auth.route('/login')
class AuthLoginResource(Resource):
    @auth.doc('login')
    @authorization.login_required
    @auth.doc(security=["jwt"])
    @auth.expect(credentials_model)
    @auth.response(401, 'Unauthorized')
    @auth.marshal_with(token_model)
    def post(self):
        """Get a JWT."""
        return {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }

@auth.route('/refresh')
class AuthRefreshResource(Resource):
    @auth.doc('refresh')
    @auth.response(401, 'Unauthorized')
    @auth.marshal_with(token_model)
    def post(self):
        """Get a new JWT. Use this when the current JWT is about to expire."""
        return {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }

if __name__ == '__main__':
    app.run(debug=True)