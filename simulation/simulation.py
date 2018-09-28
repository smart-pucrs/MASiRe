# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/CitySimulation.java

from world import World
from generator import Generator
from action_executor import ActionExecutor
from data.role import Role

class Simulation:

    def __init__(self, config):

        self.step = 0
        self.config = config
        self.world = World(config)
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config)

    def start(self):
        # creates agents and roles

        for agent in self.config['agents']:

            print(self.config['agents'][agent])

        # returns initial percepts for each agent

        return self.world.initialPercepts()

    def pre_step(self, step):
        # returns percepts for each agent

        percepts = dict()

        for agent in self.world.agents:
            
            percepts[agent.name] = self.world.percepts(agent)

        return percepts

    def step(self, actions):

        return 