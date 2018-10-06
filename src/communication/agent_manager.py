class AgentManager:

    def __init__(self):
        self.agents_list = []

    def manage_agents(self, token):
        self.agents_list.append(token)
        return self.agents_list
