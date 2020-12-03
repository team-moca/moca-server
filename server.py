import json

from flask import Flask, request, g
from flask_restx import Api, Resource, fields
from werkzeug.security import safe_str_cmp
from functools import wraps
from core.extensions import db, mqtt, pool
from dotenv import load_dotenv
import os
from apis import api

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moca.db"  # os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["MQTT_BROKER_URL"] = "localhost"
app.config["MQTT_BROKER_PORT"] = 1883
app.config["MQTT_USERNAME"] = ""
app.config["MQTT_PASSWORD"] = ""
app.config["MQTT_REFRESH_TIME"] = 1.0  # refresh time in seconds

mqtt.init_app(app)
db.init_app(app)
api.init_app(app)

mqtt.subscribe("debug/#")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(topic=message.topic, payload=message.payload.decode())
    print(data)
    pool.push(message.topic, json.loads(message.payload.decode()))


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
