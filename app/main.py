from fastapi import FastAPI
from fastapi.params import Depends
from setuptools_scm import get_version
from starlette.responses import RedirectResponse
from app.routers import auth, chats, contacts, debug, messages, users, info
from app.dependencies import oauth2_scheme
import logging

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
app.include_router(contacts.router)
app.include_router(chats.router)
app.include_router(messages.router)


@app.get("/")
async def redirect_to_docs():
    _LOGGER.info("The documentation has moved to /docs. Please use this url.")
    response = RedirectResponse(url="/docs")
    return response
