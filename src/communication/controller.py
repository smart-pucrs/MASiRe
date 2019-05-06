import time


class Controller:

    def __init__(self):
        self.agents = {}
        self.timer = time.time()
        self.simulation_response = None

    def check_population(self):
        if len(self.agents) <= 5:
            return True
        else:
            return False

    def check_timer(self):
        if time.time() - self.timer < 60:
            return True
        else:
            return False

    def check_agent(self, agent_token):
        for token in self.agents:
            if token == agent_token:
                return True

        return False
