"""
Extensions module
Each extension is initialized when app is created.
"""

from flask_sqlalchemy import SQLAlchemy
from .configurator import Configurator

db = SQLAlchemy()
configurator = Configurator()
