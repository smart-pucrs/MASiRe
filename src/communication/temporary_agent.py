
class Agent:
    def __init__(self, token, actions, url):
        self.agent_token = token
        self.actions = actions
        self.connected = False
        self.url = url
