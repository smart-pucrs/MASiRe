class AgentManager:

    def __init__(self):
        self.agents_list = []

    def manage_agents(self, token):
        """Add the agent token to the agents list"""
        self.agents_list.append(token)
        return self.agents_list
