from src.simulation.action_executor import ActionExecutor
from src.simulation.world import World
from src.simulation.generator import Generator


class Simulation:

    def __init__(self, config):
        self.step = 0
        self.config = config
        self.world = World(config)
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config)

    def start(self):
        # creates agents and roles

        self.world.events = self.generator.generateEvents()

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
