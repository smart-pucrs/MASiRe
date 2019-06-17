import time


class Controller:

    def __init__(self, qtd_agents, first_conn_time, matches, delay):
        self.connected_agents = {}
        self.agent_action = {}
        self.first_timer = None
        self.step_time = None
        self.terminated = False
        self.simulation_response = None
        self.started = False
        self.qtd_agents = int(qtd_agents)
        self.time_limit = int(first_conn_time)
        self.initial_percepts = None
        self.matches = int(matches)
        self.current_match = 1
        self.match_result = None
        self.delay = delay

    def reset_agent_action(self):
        self.agent_action.clear()

    def check_population(self):
        return len(self.connected_agents) < self.qtd_agents

    def check_timer(self):
        return time.time() - self.first_timer < self.time_limit

    def check_agent(self, agent_token):
        return agent_token in self.connected_agents

    def check_connected(self, agent_info):
        for token in self.connected_agents:
            if self.connected_agents[token].agent_info == agent_info:
                return True
        return False

    def check_agents_action(self):
        return len(self.agent_action) == self.qtd_agents

    def dif(self):
        idle_agents = []
        for agent in self.connected_agents:
            if not (agent in self.agent_action):
                idle_agents.append(agent)
        return idle_agents

    def check_matches(self):
        return self.current_match == self.matches

    def start_new_match(self):
        self.current_match += 1
        self.step_time = None
