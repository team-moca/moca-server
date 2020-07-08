from flask_restx import Api
from setuptools_scm import get_version

from .auth import api as ns_auth
from .chats import api as ns_chats

app_version = get_version()

authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
            title="MOCA Server API",
            version=app_version,
            description="REST API reference for mobile and web clients connecting to MOCA Server.",
            authorizations=authorizations,
            security=[]
        )

api.add_namespace(ns_auth, path='/auth')
api.add_namespace(ns_chats, path='/chats')