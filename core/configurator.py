import random
from connectors.telegram.config_flow import ConfigFlow

class Configurator:
    def __init__(self):
        super().__init__()
        self.active_flows = {}
        print("Initializing configurator")

    def _generate_flow_id(self):
        return "{:24x}".format(random.randint(0, 256**12))

    # TODO: supplement connector type in parameter
    def start_flow(self):
        flow_id = self._generate_flow_id()

        self.active_flows[flow_id] = ConfigFlow()

        return flow_id

    def get_flow(self, flow_id):
        return self.active_flows[flow_id]