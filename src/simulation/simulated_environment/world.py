# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data
# /WorldState.java
from simulation.simulated_environment.environment_executors.action_executor import ActionExecutor
from simulation.simulated_environment.environment_variables.agent import Agent
from simulation.simulated_environment.environment_variables.role import Role
from simulation.simulated_environment.environment_executors.generator import Generator
from simulation.simulated_environment.environment_variables.cdm import Cdm


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
        self.events = []
        self.active_events = []
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
        floods, photos, victims, water_samples = [], [], [], []

        for idx, event in enumerate(self.events):
            if idx == step:
                break
            if event['flood'] and event['flood'].active:
                floods.append(event['flood'])
                photos.extend([photo for photo in event['photos'] if photo.active])
                victims.extend([victim for victim in event['victims'] if victim.active])
                water_samples.extend([water_sample for water_sample in event['water_samples'] if water_sample.active])
        return [floods, photos, victims, water_samples]

    def get_current_event(self, step):
        flood = self.events[step]['flood']

        if not flood:
            return {}

        photos = self.events[step]['photos']
        victims = self.events[step]['victims']
        water_samples = self.events[step]['water_samples']

        for social_asset in self.events[step]['social_assets']:
            social_asset.active = True
            self.social_assets.append(social_asset)

        flood.active = True

        for photo in photos:
            photo.active = True

        for victim in victims:
            victim.active = True

        for water_sample in water_samples:
            water_sample.active = True

        return {'flood': flood, 'photos': photos, 'victims': victims, 'water_samples': water_samples}

    def decrease_period_and_lifetime(self, step):
        for i in range(step):
            prev_event = self.events[i]
            if not prev_event['flood']:
                continue

            if not prev_event['flood'].period:
                prev_event['flood'].active = False
            else:
                prev_event['flood'].period -= 1

            for victim in prev_event['victims']:
                if not victim.lifetime:
                    victim.active = False
                else:
                    victim.lifetime -= 1

    def events_completed(self):
        photos, victims, water_samples = [], [], []

        for event in self.events:
            for victim in event['victims']:
                if not victim.active and victim.lifetime:
                    victims.append(victim)

        for event in self.events:
            for photo in event['photos']:
                if not photo.active:
                    photos.append(photo)

        for event in self.events:
            for water_sample in event['water_samples']:
                if not water_sample.active:
                    water_samples.append(water_sample)

        return [victims, photos, water_samples]

    def generate_events(self):
        """
        [Method that generates the world's random events and 
        adds them to their respective category.]
        """
        self.events = self.generator.generate_events().copy()

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

    def execute_actions(self, actions, step):
        """
        [Method that parses all the actions recovered from the communication core
        and calls its execution during a step.]
        
        :param actions: A json file sent by the communication core
        containing all the actions, including the necessary parameters,
        and its respective agents.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """
        return self.action_executor.execute_actions(actions, self.cdm.location, step)
