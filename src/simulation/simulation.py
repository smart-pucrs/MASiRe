import copy
import secrets
from simulation.simulated_environment.world import World
from simulation.log_recorder import Logger


class Simulation:

    def __init__(self, config):
        """
        [Object that represents an instance of a simulation.]
        
        :param config: A json file sent by the communication core
        containing all configuration information about the simulation.
        """
        self.step = 0
        self.pre_events = None
        self.logger = Logger(config['map']['id'])
        seed = config['map']['randomSeed']
        if not seed:
            seed = secrets.token_hex(5)
        self.world = World(config, self.logger, seed)

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
        map_config = copy.deepcopy(self.world.config['map'])
        map_config_agents = copy.deepcopy(map_config)
        for key in ['steps', 'randomSeed', 'gotoCost', 'rechargeRate']:
            del map_config_agents[key]

        return [map_config_agents, self.pre_events], map_config

    def create_agent(self, token, agent_info):
        """
        [Method that generate the agent when it tries to connect to the simulation.]

        :return: A agent containing all the the information recovered from the role.
        """
        return self.world.create_agent(token, agent_info)

    def do_pre_step(self):
        """
        [Method that executes the necessary actions before a step, such as
        activating and deactivating events, and sending the percepts of 
        the current step to each agent]
        
        :return: A dict containing every agent's step percepts.
        """
        try:
            events = self.world.get_current_event(self.step)
        except IndexError:
            return None

        events.extend(self.world.percepts(self.step))
        self.world.decrease_period_and_lifetime(self.step)
        return events

    def do_step(self, actions):
        """
        [Method that executes each agent's actions.]
        
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """
        action_results = self.world.execute_actions(actions, self.step)
        self.step += 1
        self.pre_events = self.do_pre_step()

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

        results = {'action_results': action_results, 'events': self.pre_events}
        return results

    def start_new_match(self):
        self.world.reset_events()
        self.world.reset_agents()
        self.world.cdm.reset_events()
        self.step = 0
        self.pre_events = self.do_pre_step()

    def match_result(self):
        return self.world.get_agents_results()

    def agents_percepts(self):
        return self.world.agents_percepts()

    def simulation_report(self):
        return self.world.get_simulation_result()


