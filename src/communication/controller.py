import time


class Controller:

    def __init__(self):
        self.agents = {}
        self.jobs = {}
        self.timer = None

    # initializes the timer if it has not been initialized
    # check if the total agents exceeded
    def check_population(self):
        if len(self.agents.keys()) <= 5:
            return True
        else:
            return False

    # check if connection period for new agents is open
    def check_timer(self):
        if self.timer is None:
            self.timer = time.time()

        if time.time() - self.timer < 3600:
            return True
        else:
            return False

    def check_request(self, agent):
        if len(self.agents) < 5:
            if self.contain_parameters(agent):
                return True
        return False

    def contain_parameters(self, agent):
        if agent[1][1] == '' or agent[1][1] is None:
            if agent[1][2] == '' or agent[1][2] is None:
                return False
            return False

        return True

    def check_agent(self, agent):
        for ag in self.agents.keys():
            if self.agents[ag] == agent['token']:
                return True

        return False
