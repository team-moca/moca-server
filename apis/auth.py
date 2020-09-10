from flask_restx import Namespace, Resource, fields
from core.auth import auth, AuthManager
from models import User as UserModel
import hashlib
from core.extensions import db
import random

api = Namespace('auth', description="Authentication")

auth_manager = AuthManager()

credentials_model = api.model('Credentials',{
    'username': fields.String(example="jkahnwald"),
    'hash': fields.String(description="The hash can be calculated like this: sha1(username + password). Username and password must be utf-8 encoded.", example="53fab271885be6d753d501940409376b94ca7b7a"),
    'device_name': fields.String(description="The name of the device logging in. Can be a generated string based on the device properties (operating system, IP...) or a user given name.", example="MOCA Server API Playground")
})

new_user_model = api.model('NewUser',{
    'username': fields.String(example="jkahnwald"),
    'mail': fields.String(example="jkahnwald@stadt-winden.de"),
    'password': fields.String(example="supersecretpassword"),
})

verify_model = api.model('Verify',{
    'user_id': fields.Integer(example=42),
    'verification_code': fields.String(example="b18df2"),
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

@api.route('/register')
class AuthRegisterResource(Resource):
    @api.doc('register')
    @api.expect(new_user_model)
    @api.response(409, 'Conflict')
    @api.marshal_with(token_model)
    def post(self):
        """Register a new user account."""
        
        username = api.payload.get("username")
        mail = api.payload.get("mail")
        password = api.payload.get("password")
        verification_code = "{:06d}".format(random.randint(0, 999999))

        new_user = UserModel(
            username = username,
            mail = mail,
            password_hash = hashlib.sha1((username + password).encode('utf-8')).hexdigest(),
            is_verified = False,
            verification_code = verification_code
        )

        db.session.add(new_user)
        db.session.commit()

        print(f"Verification code for new user {username}: {verification_code}")
        
        return '', 201

@api.route('/verify')
class VerifyResource(Resource):
    @api.doc('verify')
    @api.expect(verify_model)
    @api.response(204, 'User verified')
    @api.response(401, 'Verification code wrong')
    def post(self):
        '''Verify a newly created user account.'''
        user_id = api.payload.get("user_id")
        verification_code = api.payload.get("verification_code")

        user = db.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        verified = verification_code == user.verification_code

        user.is_verified = verified

        db.session.commit()

        if verified:
            return '', 204
        else:
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
