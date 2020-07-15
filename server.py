from flask import Flask, request, g
from flask_restx import Api, Resource, fields
from werkzeug.security import safe_str_cmp
from functools import wraps
from core.extensions import db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moca.db' # os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

from apis import api
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)