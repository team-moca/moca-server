from fastapi import FastAPI
from fastapi.params import Depends
from setuptools_scm import get_version
from starlette.responses import RedirectResponse
from app.routers import (
    auth,
    chats,
    connectors,
    contacts,
    debug,
    messages,
    sessions,
    users,
    info,
)
from app.dependencies import mqtt
import logging
from fastapi_mqtt import FastMQTT, MQQTConfig

_LOGGER = logging.getLogger(__name__)

app = FastAPI(
    title="MOCA Server",
    description="API documentation for the MOCA mobile chat aggregator project.",
    version=get_version(),
)

app.include_router(info.router)
app.include_router(debug.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(contacts.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(connectors.router)


@app.get("/")
async def redirect_to_docs():
    _LOGGER.info("The documentation has moved to /docs. Please use this url.")
    response = RedirectResponse(url="/docs")
    return response


@app.on_event("startup")
async def startapp():
    await mqtt.connection()


@app.on_event("shutdown")
async def shutdown():
    await mqtt.client.disconnect()


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("moca/#")  # subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)
