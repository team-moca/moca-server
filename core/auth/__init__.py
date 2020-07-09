from flask_httpauth import HTTPTokenAuth
import jwt
from datetime import datetime, timedelta

auth = HTTPTokenAuth(scheme='Bearer')
secret = "J7rSEi4tVSB2tdRpubRRWQj5C3s5RwCC"

users = {
    'jkahnwald': 'd82cd9650672484e27eb8413a4d6b30018741b6e'
}

invalidated_jtis = []

class AuthManager:
    def __init__(self):
        self.jti = 0


    def login(self, username, pw_hash, device_name):
        if users.get(username) == pw_hash:
            self.jti = self.jti + 1
            return jwt.encode({
                'username': username,
                'device_name': device_name,
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow(),
                'jti': self.jti
                }, secret, algorithm='HS256')

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