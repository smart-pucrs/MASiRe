import time


class Controller:

    def __init__(self, qtd_agents):
        self.agents = {}
        self.timer = None
        self.simulation_response = None
        self.qtd_agents = int(qtd_agents)

    def check_population(self):
        if len(self.agents) < self.qtd_agents:
            return True
        else:
            return False

    def check_timer(self):
        if self.timer is None:
            self.timer = time.time()

        if time.time() - self.timer < 40:
            return True
        else:
            return False

    def check_agent(self, agent_token):
        for token in self.agents:
            if token == agent_token:
                return True

        return False