# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from src.simulation.simulated_enviroment.environment_executors.action_executor import ActionExecutor
from src.simulation.simulated_enviroment.environment_variables.agent import Agent
from src.simulation.simulated_enviroment.environment_variables.role import Role
from src.simulation.simulated_enviroment.environment_executors.generator import Generator
from src.simulation.simulated_enviroment.environment_variables.cdm import Cdm


class World:

    def __init__(self, config):
        """
        [Object that represents the simulation universe.]

        :param config: The configuration archive received by the
        communication core.
        """
        self.config = config
        self.events = []
        self.roles = {}
        self.agents = {}
        self.floods = []
        self.water_samples = []
        self.photos = []
        self.victims = []
        self.agent_counter = 0
        self.free_roles = []
        self.cdm = Cdm([config['map']['centerLat'], config['map']['centerLon']])
        self.generator = Generator(config)
        self.action_executor = ActionExecutor(config, self)

    def percepts(self, step):
        if step <= 0:
            return [], [], [], [], []

        # Get all active floods
        floods = []
        for idx, flood in enumerate(self.events):
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

        return floods, water_samples, photos, victims

    def percepts_by_step(self, step):
        """
        [Method that generates each step's percepts.]
        
        :param step: The step number the simulation is in
        :return: Three lists, each one containing information about
        the active events of the simulation and one Flood object
        """
        if self.events[step] is None:
            return []

        else:
            flood = self.events[step]
            water_samples = [water_sample for water_sample in flood.water_samples if water_sample.active]
            photos = [photo for photo in flood.photos if photo.active]
            victims = [victim for victim in flood.victims if victim.active]
            return flood, water_samples, photos, victims

    def generate_events(self):
        """
        [Method that generates the world's random events and 
        adds them to their respective category.]
        """
        self.events = self.generator.generate_events()

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
            self.roles[role] = Role(role, self.config['roles'])

        for role in self.config['agents']:
            role = [role] * self.config['agents'][role]
            self.free_roles.extend(role)

    def create_agent(self, token):
        """
        [Method creates list containing each role times the amount of agents
        it should have and assign one randomly chosen role to the given token]

        :return: A agent containing all the information recovered from the role
        """
        role = self.free_roles[self.agent_counter]
        agent = Agent(token, self.roles[role], role)
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
