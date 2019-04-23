from simulation.simulated_enviroment.world import World
from simulation.log_recorder import Logger


class Simulation:

    def __init__(self, config):
        """
        [Object that represents an instance of a simulation.]
        
        :param config: A json file sent by the communication core
        containing all configuration information about the simulation.
        """
        self.step = 0
        self.world = World(config)
        self.pre_events = None
        self.logger = Logger(config['map']['id'])

    def start(self):
        """
        [Method that starts the simulation, generating random events, 
        creating roles, agents and initial percepts.]
        
        :return: A list containing the simulation's agents, and a list
        containing the agent's initial percepts.
        """
        self.world.generate_events()
        roles = self.world.create_roles()
        agent_percepts, full_percepts = self.initial_percepts()

        self.logger.register_perceptions(percepts=full_percepts, roles=roles,
                                         agent_percepts=agent_percepts, seed=full_percepts['randomSeed'])
        return agent_percepts

    def initial_percepts(self):
        self.pre_events = self.do_pre_step()
        map_config = self.world.config['map']
        map_config_agents = map_config.copy()
        for key in ['steps', 'randomSeed', 'gotoCost', 'rechargeRate']:
            del map_config_agents[key]
        return map_config_agents, map_config

    def create_agent(self, token):
        """
        [Method that generate the agent when it tries to connect to the simulation.]

        :return: A agent containing all the the information recovered from the role.
        """
        return self.world.create_agent(token)

    def do_pre_step(self):
        """
        [Method that executes the necessary actions before a step, such as
        activating and deactivating events, and sending the percepts of 
        the current step to each agent]
        
        :return: A dict containing every agent's step percepts.
        """

        try:
            event = self.world.events[self.step]
        except IndexError:
            return None
        pending_events = self.world.percepts(self.step)

        if event:
            self.world.events[self.step].active = True
            for water_sample in event.water_samples:
                water_sample.active = True
                self.world.water_samples.append(water_sample)

            for photo in event.photos:
                photo.active = True
                self.world.photos.append(photo)

            for victim in event.victims:
                victim.active = True
                self.world.victims.append(victim)

        return {'current_event': event, 'pending_events': pending_events}

    def do_step(self, actions):
        """
        [Method that executes each agent's actions.]
        
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """
        if self.pre_events is None:
            total_floods = self.world.generator.total_floods
            total_victims = self.world.generator.total_victims
            total_photos = self.world.generator.total_photos
            total_water_samples = self.world.generator.total_water_samples
            completed_tasks = self.world.events_completed()

            self.logger.register_end_of_simulation(
                total_floods,
                total_victims,
                total_photos,
                total_water_samples,
                self.step-1,
                completed_tasks
            )

            return 'Simulation Ended'

        action_results = self.world.execute_actions(actions)
        results = {'action_results': action_results, 'events': self.pre_events.copy()}
        self.step += 1
        self.pre_events = self.do_pre_step()
        return results
