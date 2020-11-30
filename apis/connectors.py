import time

from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import GatewayTimeout

from core.auth import auth
from core.exceptions import MocaException, TimeoutException
from core.extensions import db, configurator, mqtt, pool
from models import Connector as ConnectorModel
from models import Contact as ContactModel
from models import User as UserModel

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

        mqtt.publish(f"telegram/configure/{flow_id}", json.dumps(api.payload))

        try:
            response = pool.get(f"telegram/configure/{flow_id}/response")
        except TimeoutException as e:
            e = GatewayTimeout()
            e.data = {"code": "GATEWAY_TIMEOUT"}
            raise e
        finally:
            mqtt.unsubscribe(f"telegram/configure/{flow_id}/response")

        if response.get("step") == "finished":

            # 1. Get user id
            user_id = auth.current_user().get("payload", {}).get("user_id")

            # Check if user not already has a connection
            if (
                db.session.query(ConnectorModel)
                .filter(ConnectorModel.user_id == user_id)
                .count()
                == 0
            ):

                contact = response.get("data", {}).get("contact")

                # 2. Create contact
                new_contact = ContactModel(
                    service_id="TELEGRAM",
                    name=contact.get("name"),
                    username=contact.get("username"),
                    phone=contact.get("phone"),
                    user_id=user_id,
                )
                db.session.add(new_contact)

                # 3. Create connector
                new_connector = ConnectorModel(
                    connector_type="TELEGRAM",
                    user_id=user_id,
                    connector_user_id=contact.get("id"),
                    configuration="",
                )
                db.session.add(new_connector)

                db.session.commit()

            else:
                print("Configuration already exists.")

        return response, 200
