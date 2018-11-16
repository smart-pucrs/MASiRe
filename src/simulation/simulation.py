from src.simulation.world import World


class Simulation:

    def __init__(self, config):
        """
        []

        :param config:
        """
        self.step = 0
        self.config = config
        self.world = World(config)

    def start(self):
        self.world.generate_events()
        self.world.create_roles()

        return self.world.create_agents(), self.world.initial_percepts()

    def do_pre_step(self):
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
        action_results = self.world.execute_actions(actions)
        self.step += 1

        return action_results
