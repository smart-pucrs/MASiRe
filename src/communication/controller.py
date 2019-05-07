import time


class Controller:

    def __init__(self, qtd_agents, first_conn_time):
        self.agents = {}
        self.first_timer = time.time()
        self.step_time = None
        self.terminated = False
        self.simulation_response = None
        self.qtd_agents = int(qtd_agents)
        self.time_limit = int(first_conn_time)

    def check_population(self):
        return len(self.agents) < self.qtd_agents

    def check_timer(self):
        return time.time() - self.first_timer < self.time_limit

    def check_agent(self, agent_token):
        return agent_token in self.agents

    def check_connected(self, agent_info):
        for token in self.agents:
            if self.agents[token].agent_info == agent_info:
                return True

        return False
