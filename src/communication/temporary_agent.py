
class Agent:
    def __init__(self, token, obj):
        self.agent_token = token
        self.action_name = None
        self.action_param = None
        self.connected = False
        self.sent_obj = obj
