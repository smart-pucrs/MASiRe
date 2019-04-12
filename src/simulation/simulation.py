from src.simulation.simulated_enviroment.world import World


class Simulation:

    def __init__(self, config):
        """
        [Object that represents an instance of a simulation.]
        
        :param config: A json file sent by the communication core
        containing all configuration information about the simulation.
        """
        self.step = 0
        self.world = World(config)

    def start(self):
        """
        [Method that starts the simulation, generating random events, 
        creating roles, agents and initial percepts.]
        
        :return: A list containing the simulation's agents, and a list
        containing the agent's initial percepts.
        """
        self.world.generate_events()
        self.world.create_roles()
        return self.initial_percepts()

    def initial_percepts(self):
        events = self.do_pre_step()
        map_config = self.world.config['map']
        for key in ['steps', 'randomSeed', 'gotoCost', 'rechargeRate']:
            del map_config[key]
        return {'events': events, 'map_config': map_config}

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

        event = self.world.events[self.step]
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

        return {'current_events': str(event)}, {'pending_events': pending_events}

    def do_step(self, actions):
        """
        [Method that executes each agent's actions.]
        
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """
        action_results = self.world.execute_actions(actions)
        self.step += 1
        return {'action_results': action_results, 'events': self.do_pre_step()}
