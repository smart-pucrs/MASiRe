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
        self.world.create_agents()
        self.world.initial_percepts()

    def do_pre_step(self):
        """
        [Method that executes the necessary actions before a step, such as
        activating and deactivating events, and sending the percepts of 
        the current step to each agent]
        
        :return: A dict containing every agent's step percepts.
        """

        self.world.active_events = [event for event in self.world.active_events if
                                    event[0] + event[1].period >= self.step]

        event_step = self.world.events[self.step]

        if event_step:
            self.world.active_events.append((self.step, event_step))

            for water_sample in event_step:
                water_sample.active = True
                self.world.water_samples.append(water_sample)

            for photo in flood.photos:
                photo.active = True
                self.world.photos.append(photo)

                for victim in photo.victims:
                    victim.active = True
                    self.world.victims.append(victim)

        percepts = dict()

        for agent in self.world.agents.values():
            percepts[agent.id] = self.world.percepts(agent)

        return percepts

    def do_step(self, actions):
        """
        [Method that executes each agent's actions.]
        
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """
        action_results = self.world.execute_actions(actions)
        self.step += 1

        return action_results
