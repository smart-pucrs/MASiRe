import time


class Controller:

    def __init__(self):
        self.agents = []
        self.timer = None

    def check_population(self):
        if len(self.agents) <= 5:
            return True
        else:
            return False

    def check_timer(self):
        if self.timer is None:
            self.timer = time.time()

        if time.time() - self.timer < 10:
            return True
        else:
            return False

    def check_agent(self, agent):
        for ag in self.agents:
            if self.agents[ag] == agent['token']:
                return True

        return False
