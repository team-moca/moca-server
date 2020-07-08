from flask_restx import Namespace, Resource, fields
from core.auth import auth

api = Namespace('auth', description="Authentication")

credentials_model = api.model('Credentials',{
    'username': fields.String(example="jkahnwald"),
    'hash': fields.String(description="The hash can be calculated like this: sha1(username + password). Username and password must be utf-8 encoded.")
})

token_model = api.model('Token', {
    'token': fields.String(description="A JWT token that can be used to access restricted resources.")
})

@api.route('/login')
class AuthLoginResource(Resource):
    @api.doc('login')
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.expect(credentials_model)
    @api.response(401, 'Unauthorized')
    @api.marshal_with(token_model)
    def post(self):
        """Get a JWT."""
        return {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }

@api.route('/refresh')
class AuthRefreshResource(Resource):
    @api.doc('refresh')
    @api.response(401, 'Unauthorized')
    @api.marshal_with(token_model)
    def post(self):
        """Get a new JWT. Use this when the current JWT is about to expire."""
        return {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }
