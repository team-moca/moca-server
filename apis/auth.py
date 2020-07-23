from flask_restx import Namespace, Resource, fields
from core.auth import auth, AuthManager

api = Namespace('auth', description="Authentication")

auth_manager = AuthManager()

credentials_model = api.model('Credentials',{
    'username': fields.String(example="jkahnwald"),
    'hash': fields.String(description="The hash can be calculated like this: sha1(username + password). Username and password must be utf-8 encoded.", example="53fab271885be6d753d501940409376b94ca7b7a"),
    'device_name': fields.String(description="The name of the device logging in. Can be a generated string based on the device properties (operating system, IP...) or a user given name.", example="MOCA Server API Playground")
})

token_model = api.model('Token', {
    'token': fields.String(description="A JWT token that can be used to access restricted resources.")
})

@api.route('/login')
class AuthLoginResource(Resource):
    @api.doc('login')
    @api.expect(credentials_model)
    @api.response(401, 'Unauthorized')
    @api.marshal_with(token_model)
    def post(self):
        """Get a JWT."""
        token = auth_manager.login(api.payload.get('username'), api.payload.get('hash'), api.payload.get('device_name'))
        if token:
            return { 'token': token.decode() }
        
        return '', 401

@api.route('/refresh')
class AuthRefreshResource(Resource):
    @api.doc('refresh')
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.response(401, 'Unauthorized')
    @api.marshal_with(token_model)
    def post(self):
        """Get a new JWT. Use this when the current JWT is about to expire."""
        return { 'token': auth_manager.refresh(auth.current_user().get("token")).decode() }
