
class Agent:
    def __init__(self, token, counter, actions):
        self.external_id = token
        self.internal_id = counter
        self.actions = actions
        self.connected = False
