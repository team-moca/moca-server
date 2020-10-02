from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.extensions import db, configurator
from models import Connector as ConnectorModel
import json

api = Namespace('connectors', description='Connector operations')

step_model = api.model('ConnectorConfigFlowStep', {
    'ignore_this_field': fields.String,
})

@api.route('/')
class ConnectorsResource(Resource):

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("add_connector")
    @api.response(200, 'Flow started')
    def post(self, **kwargs):
        """Send a connector to a chat."""

        return { "flow_id": configurator.start_flow() }, 200

@api.route('/<string:flow_id>')
class ConnectorsResource(Resource):

    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("step")
    @api.expect(step_model)
    @api.response(200, 'Step correct')
    def post(self, flow_id, **kwargs):
        """Submit a step of the current configuration flow."""

        flow = configurator.get_flow(flow_id)

        return flow.current_step(api.payload), 200

