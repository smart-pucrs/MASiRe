# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from src.simulation.simulated_enviroment.environment_executors.action_executor import ActionExecutor
from src.simulation.simulated_enviroment.environment_variables.agent import Agent
from src.simulation.simulated_enviroment.environment_variables.role import Role
from src.simulation.simulated_enviroment.environment_executors.generator import Generator
from src.simulation.simulated_enviroment.environment_executors.cdm import Cdm


class World:

    def __init__(self, config):
        """
        [Object that represents the simulation universe.]

        :param config: The configuration archive received by the
        communication core.
        """
        self.config = config
        self.events = []
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
        self.generate_events()
        self.action_executor = ActionExecutor(config, self)

    def initial_percepts(self):
        """
        [Defines the initial percepts of the simulation to all agents.]

        :return: ?
        """
        # what should be sent to the agents on the initial percepts?
        return []

    def percepts(self, agent):
        """
        [Method that generates each step's percepts.]
        
        :param agent: An object representing the agent to which
        the percepts should be generated to.
        :return: Four lists, each one containing information about
        the active events of the simulation
        """
        
        floods, water_samples, photos, victims = [], [], [], []

        for flood in self.floods:
            if flood.active:
                floods.append(flood)

        for water_sample in self.water_samples:
            if water_sample.active:
                water_samples.append(water_sample)

        for photo in self.photos:
            if photo.active:
                photos.append(photo)

        for victim in self.victims:
            if victim.active:
                victims.append(victim)

        return floods, water_samples, photos, victims, agent

    def generate_events(self):
        """
        [Method that generates the world's random events and 
        adds them to their respective category.]
        """
        
        self.events, self.router = self.generator.generate_events()

        for flood in self.events:
            if flood is None:
                continue

            self.floods.append(flood)

            for water_sample in flood.water_samples:
                self.water_samples.append(water_sample)

            for photo in flood.photos:
                if photo is not None:

                    self.photos.append(photo)

                    for victim in photo.victims:
                        self.victims.append(victim)

    def create_roles(self):
        """
        [Method that generates the agent's roles.]
        """
        for role in self.config['roles']:
            self.roles[role] = Role(role, self.config)

    def create_agents(self):
        """
        [Method that generates the world's random events and 
        adds them to their respective category.]

        :return: A list containing each agent's IDs
        """
        for role in self.config['agents']:
            agents_number = self.config['agents'][role]

            for _ in range(agents_number):
                self.create_agent(role)

        return list(self.agents.values())

    def create_agent(self, role):
        """
        [Method that creates an agent with a specific role.]

        :param role: A string indicating the role of the agent
        to be created.
        :return: A list containing each agent's IDs.
        """

        self.agent_counter += 1
        self.agents[self.agent_counter] = Agent(self.agent_counter, self.roles[role])

    def execute_actions(self, actions):
        """
        [Method that parses all the actions recovered from the communication core
        and calls its execution during a step.]
        
        :param actions: A json file sent by the communication core
        containing all the actions, including the necessary parameters,
        and its respective agents.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """

        return self.action_executor.execute_actions(actions)

    def create_route_coordinate(self, start, location):
        # create route between location START and LOCATION
        # both are a list -> [lat, long]

        # self.router.
        return
