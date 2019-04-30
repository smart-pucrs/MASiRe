
class Agent:
    def __init__(self, token, obj):
        self.agent_token = token
        self.action = ()
        self.action_name = ""
        self.action_param = []
        self.connected = False
        self.sent_obj = obj
