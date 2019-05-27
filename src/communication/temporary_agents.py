
class JobSenderAgent:
    def __init__(self):
        self.action_name = None
        self.action_param = None


class ConnectedAgent:
    def __init__(self, token, obj):
        self.token = token
        self.connected = False
        self.agent_info = obj
        self.simulation_agent = None
