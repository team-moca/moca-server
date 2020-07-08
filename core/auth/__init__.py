from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImprYWhud2FsZCIsImlhdCI6MTUxNjIzOTAyMn0.meNzV4ABOhmN_CxmzBkzTH1m4gpdEv3vrJBl89dllgY': 'jkahnwald'
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

@auth.error_handler
def authorization_error(status):
    return {'message': 'Unauthorized'}, status