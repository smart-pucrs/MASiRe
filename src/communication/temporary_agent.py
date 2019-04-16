
class Agent:
    def __init__(self, token, url):
        self.agent_token = token
        self.url = url
        self.action_name = None
        self.action_param = None
        self.connected = False
