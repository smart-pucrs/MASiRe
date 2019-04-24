# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from simulation.simulated_enviroment.environment_executors.action_executor import ActionExecutor
from simulation.simulated_enviroment.environment_variables.agent import Agent
from simulation.simulated_enviroment.environment_variables.role import Role
from simulation.simulated_enviroment.environment_executors.generator import Generator
from simulation.simulated_enviroment.environment_variables.cdm import Cdm


class World:

    def __init__(self, config, logger):
        """
        [Object that represents the simulation universe.]

        :param config: The configuration archive received by the
        communication core.
        """
        self.config = config
        self.roles = {}
        self.agents = {}
        self.floods = []
        self.water_samples = []
        self.photos = []
        self.victims = []
        self.social_assets = []
        self.agent_counter = 0
        self.free_roles = []
        self.cdm = Cdm([config['map']['centerLat'], config['map']['centerLon']])
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config, self, logger)

    def percepts(self, step):
        if step == 0:
            return [[], [], [], [], []]

        # Get all active floods
        floods = []
        for idx, flood in enumerate(self.floods):
            if idx == step - 1:
                break
            if flood and flood.active:
                floods.append(flood)

        # Get all pending water_sample
        water_samples = []
        for idx, water_sample in enumerate(self.water_samples):
            if idx == step - 1:
                break
            if water_sample.active:
                water_samples.append(water_sample)

        # Get all pending photo
        photos = []
        for idx, photo in enumerate(self.photos):
            if idx == step - 1:
                break
            if photo.active:
                photos.append(photo)

        # Get all pending victims
        victims = []
        for idx, victim in enumerate(self.victims):
            if idx == step - 1:
                break
            if victim.active:
                victims.append(victim)

        return [floods, water_samples, photos, victims]

    def events_completed(self):
        victims = [victim for victim in self.victims if not victim.active and not victim.in_photo]
        photos = [photo for photo in self.photos if not photo.active]
        water_samples = [water_sample for water_sample in self.water_samples if not water_sample.active]
        return [victims, photos, water_samples]

    def generate_events(self):
        """
        [Method that generates the world's random events and 
        adds them to their respective category.]
        """
        self.floods = self.generator.generate_events().copy()

    def create_roles(self):
        """
        [Method that generates the agent's roles.]
        """
        for role in self.config['roles']:
            self.roles[role] = Role(role, self.config['roles'])

        for role in self.config['agents']:
            role = [role] * self.config['agents'][role]
            self.free_roles.extend(role)

        return set(self.free_roles)

    def create_agent(self, token, agent_info):
        """
        [Method creates list containing each role times the amount of agents
        it should have and assign one randomly chosen role to the given token]

        :return: A agent containing all the information recovered from the role
        """
        role = self.free_roles[self.agent_counter]
        agent = Agent(token, self.roles[role], role, self.cdm.location, agent_info)
        self.agents[token] = agent
        self.agent_counter += 1
        return agent

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
        return self.action_executor.execute_actions(actions, self.cdm.location)
