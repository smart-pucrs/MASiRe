from action_executor import ActionExecutor
from world import World
from generator import Generator


class Simulation:

    def __init__(self, config):
        self.step = 0
        self.config = config
        self.world = World(config)
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config)

    def start(self):
        # creates agents and roles

        self.world.events = self.generator.generate_events()

        print(self.world.events)

        agents = []

        for agent_type in self.config['agents']:

            agents_number = self.config['agents'][agent_type]

            for x in range(agents_number):

                agents.append(self.world.create_agent(agent_type))

        return (agents, self.world.initial_percepts())

    def pre_step(self, step):
        # returns percepts for each agent

        percepts = dict()

        for agent in self.world.agents:
            
            percepts[agent.name] = self.world.percepts(agent)

        return percepts

    def step(self, actions):

        return 
