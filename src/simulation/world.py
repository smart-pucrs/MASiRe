# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from src.simulation.action_executor import ActionExecutor
from src.simulation.data.agent import Agent
from src.simulation.data.role import Role
from src.simulation.generator import Generator

class World:

    def __init__(self, config):

        self.config = config
        self.events = None
        self.cdm = cdm
        self.roles = dict()
        self.agents = dict()
        self.agent_counter = 0
        self.active_events = []
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config, self)

    def initial_percepts(self):
        return []

    def percepts(self, agent):
        return []

    def generate_events(self):
        self.events = self.generator.generate_events()

        '''for flood in events: 
            self.floods.append(flood)

            for water_sample in flood.water_samples:
                self.water_samples.append(water_sample)

            for photo in flood.photos:
                self.photos.append(photo)

                for victim in photo.victims:
                    self.victims.append(victim)'''

    def create_roles(self):
        for role in self.config['roles']:
            
            self.roles[role] = Role(role, self.config)

    def create_agents(self):
        for role in self.config['agents']:
            agents_number = self.config['agents'][role]

            for x in range(agents_number):
                self.create_agent(role)

        return list(self.agents.values())

    def create_agent(self, role):
        # in the future this method should also generate info about the agents location (i think)
        self.agent_counter += 1
        self.agents[self.agent_counter] = Agent(self.agent_counter, self.roles[role])

    def execute_actions(self, actions):
        return self.action_executor.execute_actions(self, actions)
