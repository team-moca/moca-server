import hashlib
import random

from flask_httpauth import HTTPTokenAuth
import jwt
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from core.extensions import db
from models import User as UserModel
from core.exceptions import UserNotVerifiedException, InvalidAuthException, UsernameAlreadyTakenException

auth = HTTPTokenAuth(scheme='Bearer')
secret = "J7rSEi4tVSB2tdRpubRRWQj5C3s5RwCC"

invalidated_jtis = []


class AuthManager:
    def __init__(self):
        self.jti = 0

    def login(self, username, pw_hash, device_name):

        user = db.session.query(UserModel).filter(UserModel.username == username).first()

        # Only allow login if the user is verified
        if user and not user.is_verified:
            raise UserNotVerifiedException(f"User {user.username} is not yet verified.")

        if user and user.password_hash == pw_hash:

            self.jti = self.jti + 1
            return jwt.encode({
                'username': username,
                'user_id': user.user_id,
                'device_name': device_name,
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow(),
                'jti': self.jti
                }, secret, algorithm='HS256')

        raise InvalidAuthException("Username or password wrong.")

    def refresh(self, token):
        payload = jwt.decode(token, secret, algorithms=['HS256'])

        invalidated_jtis.append(payload.get('jti'))

        self.jti = self.jti + 1
        payload.update({
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'jti': self.jti
        })
        return jwt.encode(payload, secret, algorithm='HS256')

    def register(self, username, mail, password):
        verification_code = "{:06d}".format(random.randint(0, 999999))

        try:
            new_user = UserModel(
                username=username,
                mail=mail,
                password_hash=hashlib.sha1((username + password).encode('utf-8')).hexdigest(),
                is_verified=False,
                verification_code=verification_code
            )

            db.session.add(new_user)
            db.session.flush()
        except IntegrityError as ie:
            db.session.rollback()

            raise UsernameAlreadyTakenException(f"A user with the name {username} already exists. Choose another "
                                                f"username.")
        else:
            db.session.commit()

        print(f"Verification code for new user {username}: {verification_code}")

@auth.verify_token
def verify_token(token):
    if token:
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            if payload.get('jti') not in invalidated_jtis:
                return {
                    "token": token,
                    "payload": payload
                }
        except jwt.ExpiredSignatureError:
            pass


@auth.error_handler
def authorization_error(status):
    return {'message': 'Unauthorized'}, status
