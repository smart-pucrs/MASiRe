# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/CitySimulation.java

from world import *
from generator import *
from action_executor import *


class Simulation:

    def __init__(self, config):
        self.step = 0
        self.world = World(config)
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config)

    def start(self):
        # returns initial percepts for each agent

        return self.world.initialPercepts()

    def pre_step(self, step):
        # returns percepts for each agent

        percepts = dict()

        for agent in self.world.agents:
            percepts[agent.name] = self.world.percepts(agent)

        return percepts
