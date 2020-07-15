from flask_restx import Api

from .auth import api as ns_auth
from .chats import api as ns_chats
from .messages import api as ns_messages
from .info import api as ns_info
from .debug import api as ns_debug
from core.version_helper import app_version

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

api.add_namespace(ns_info, path='/info')
api.add_namespace(ns_debug, path='/debug')
api.add_namespace(ns_auth, path='/auth')
api.add_namespace(ns_chats, path='/chats')
api.add_namespace(ns_messages, path='/chats')