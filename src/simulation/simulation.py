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

        self.world.events = self.generator.generateEvents()

        agents = []

        for agent_type in self.config['_types']:

            agents_number = self.config['agents'][agent_type]

            for x in range(agents_number):

                agents.append(self.world.create_agent(agent_type))

        return (agents, self.world.initialPercepts())

    def pre_step(self, step):
        # returns percepts for each agent

        percepts = dict()

        for agent in self.world.agents:
            
            percepts[agent.name] = self.world.percepts(agent)

        return percepts

    def step(self, actions):

        return 
