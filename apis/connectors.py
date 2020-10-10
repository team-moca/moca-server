import time

from flask_restx import Namespace, Resource, fields
from core.auth import auth
from core.exceptions import MocaException
from core.extensions import db, configurator, mqtt, pool
from models import Connector as ConnectorModel
import json

api = Namespace("connectors", description="Connector operations")

step_model = api.model(
    "ConnectorConfigFlowStep",
    {
        "ignore_this_field": fields.String,
    },
)


@api.route("/")
class ConnectorsResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("add_connector")
    @api.response(200, "Flow started")
    def post(self, **kwargs):
        """Send a connector to a chat."""

        flow_id = configurator.start_flow()

        return {"flow_id": flow_id}, 200


@api.route("/<string:flow_id>")
class ConnectorsResource(Resource):
    @auth.login_required
    @api.doc(security=["jwt"])
    @api.doc("step")
    @api.expect(step_model)
    @api.response(200, "Step correct")
    def post(self, flow_id, **kwargs):
        """Submit a step of the current configuration flow."""

        mqtt.subscribe(f"telegram/configure/{flow_id}/response")
        pool.listen(f"telegram/configure/{flow_id}/response")

        mqtt.publish(f"telegram/configure/{flow_id}")

        try:
            response = pool.get(f"telegram/configure/{flow_id}/response")
        except MocaException as e:
            return {
                       "error": {
                           "code": e.error_code,
                           "message": getattr(e, "message", repr(e)),
                       }
                   }, e.http_code
        finally:
            mqtt.unsubscribe(f"telegram/configure/{flow_id}/response")

        return response, 200
