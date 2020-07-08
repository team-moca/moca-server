from flask import Flask, request
from flask_restx import Api, Resource, fields
from werkzeug.security import safe_str_cmp
from functools import wraps
from apis import api

app = Flask(__name__)
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)