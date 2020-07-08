from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.version_helper import app_version

api = Namespace('info', description="General server information")

info_model = api.model('ServerInfo', {
    'version': fields.String(description="A semantic versioning number representing the current api version."),
    'last_supported_version': fields.String(description="A semantic versioning number representing the last api version clients must have to connect to the server.")
})

@api.route('')
class InfoResource(Resource):
    @api.doc('info')
    @api.marshal_with(info_model)
    def get(self):
        """Get server  information."""
        return {
            'version': app_version,
            'last_supported_version': app_version,
        }
