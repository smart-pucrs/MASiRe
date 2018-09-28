# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/WorldState.java
from src.simulation.data.agent import Agent


class World:

    def __init__(self, config):

        self.agent_counter = 0
        self.agents = dict()

    def initial_percepts(self):

        return []

    def percepts(self, agent):

        return []

    def create_agent(self, agent_type):

        # in the future this method should also generate info about the agents location (i think)
        self.agent_counter += 1
        return Agent(self.agent_counter, agent_type)
