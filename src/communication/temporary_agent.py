
class Agent:
    def __init__(self, token, obj):
        self.token = token
        self.action_name = None
        self.action_param = None
        self.connected = False
        self.agent_info = obj
