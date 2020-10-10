"""
Extensions module
Each extension is initialized when app is created.
"""

from flask_sqlalchemy import SQLAlchemy
from .configurator import Configurator
from flask_mqtt import Mqtt
from .pool import Pool

db = SQLAlchemy()
configurator = Configurator()
mqtt = Mqtt()
pool = Pool()
