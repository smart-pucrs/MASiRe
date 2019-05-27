
class JobSenderAgent:
    def __init__(self):
        self.action_name = None
        self.action_param = None
        self.connected = False


class ConnectedAgent:
    def __init__(self, token, obj, namespace):
        self.token = token
        self.connected = False
        self.agent_info = obj
        self.namespace = namespace
