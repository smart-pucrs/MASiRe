import time


class Controller:

    def __init__(self, qtd_agents, first_conn_time):
        self.agents = {}
        self.timer = time.time()
        self.simulation_response = None
        self.qtd_agents = int(qtd_agents)
        self.time_limit = int(first_conn_time)

    def check_population(self):
        if len(self.agents) < self.qtd_agents:
            return True
        else:
            return False

    def check_timer(self):
        if time.time() - self.timer < self.time_limit:
            return True
        else:
            return False

    def check_agent(self, agent_token):
        return agent_token in self.agents

    def check_connected(self, agent_info):
        for token in self.agents:
            if self.agents[token].agent_info == agent_info:
                return True

        return False
