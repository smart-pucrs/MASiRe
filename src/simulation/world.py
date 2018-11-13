# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from src.simulation.action_executor import ActionExecutor
from src.simulation.data.agent import Agent
from src.simulation.data.role import Role
from src.simulation.generator import Generator
from src.simulation.data.cdm import Cdm

class World:

    def __init__(self, config):
        """
        [Object that represents the simulation universe.]

        :param config: The configuration archive received by the
        communication core.
        """
        self.config = config
        self.events = None
        self.roles = dict()
        self.agents = dict()
        self.agent_counter = 0
        self.active_events = []
        self.floods = []
        self.water_samples = []
        self.photos = []
        self.victims = []
        self.cdm = Cdm([config['map']['centerLat'], config['map']['centerLon']])
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config, self)
        self.router = None

    def initial_percepts(self):
        """
        [Defines the initial percepts of the simulation to all agents.]

        :return: ?
        """
        # what should be sent to the agents on the initial percepts?
        return []

    def percepts(self, agent):
        floods, water_samples, photos, victims = [], [], [], []

        for flood in self.floods:
            if flood.active: floods.append(flood)

        for water_sample in self.water_samples:
            if water_sample.active: water_samples.append(water_sample)

        for photo in self.photos:
            if photo.active: photos.append(photo)

        for victim in self.victims:
            if victim.active: victims.append(victim)

        return floods, water_samples, photos, victims

    def generate_events(self):
        print("----")

        self.events, self.router = self.generator.generate_events()
        # temp = self.router.routing_states
        # temp1 = self.router.original_state

        for flood in self.events:
            self.floods.append(flood)

            for water_sample in flood.water_samples:
                self.water_samples.append(water_sample)

            for photo in flood.photos:
                self.photos.append(photo)

                for victim in photo.victims:
                    self.victims.append(victim)

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
        return self.action_executor.execute_actions(actions)

    def create_route_coordinate(start, location):
        # create route between location START and LOCATION
        # both are a list -> [lat, long]
        return
