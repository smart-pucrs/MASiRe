from simulation_engine.simulation_helpers.cycle import Cycle
from simulation_engine.simulation_helpers.logger import Logger


class Simulation:
    """Class that represents the engine of the simulation, connecting agents and social assets, doing steps and saving
    log information."""

    def __init__(self, config, load_sim, write_sim):
        self.cycler = Cycle(config, load_sim, write_sim)
        self.terminated = False
        self.actions_amount = 0
        self.actions_amount_by_step = []
        self.actions_by_step = []
        self.action_token_by_step = []

    def connect_agent(self, token):
        """Connect the agent to the simulation.

        :param token: The identifier of the agent.
        :return bool: True if the agent was connected else False."""

        return self.cycler.connect_agent(token)

    def connect_social_asset(self, main_token, token):
        """Connect the social asset to the simulation.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was connected else False."""

        return self.cycler.connect_social_asset(main_token, token)

    def finish_social_assets_connections(self, tokens):
        return self.cycler.finish_social_assets_connections(tokens)

    def disconnect_agent(self, token):
        """Disconnect the agent from the simulation.

        :param token: The identifier of the agent.
        :return bool: True if the agent was connected else False."""

        return self.cycler.disconnect_agent(token)

    def disconnect_social_asset(self, token):
        """Disconnect the social asset from the simulation.

        :param token: The identifier of the social asset.
        :return bool: True if the agent was connected else False."""

        return self.cycler.disconnect_social_asset(token)

    def start(self):
        """Start the simulation by activating the first step and returning all the connected agents and social assets
        information saved back to them along with the current step.

        :return tuple: First position holding the agents, second position the social assets and the third holding
        the current step."""

        self.cycler.activate_step()
        self.cycler.current_step += 1
        agents = self.cycler.get_active_agents_info()
        step = self.cycler.get_step()

        if self.cycler.check_steps():
            self.terminated = True
            return agents, step

        self.cycler.activate_step()
        map_percepts = self.get_map_percepts()

        return agents, step, self.cycler.current_step, map_percepts

    def restart(self, config_file, load_sim, write_sim):
        """Restart the simulation by regenerating all the simulation and reseting all the log variables.

        :return tuple: First position holding the agents, second position the social assets, third position holding
        the current step, fourth position holding the report for previous match and the the fifth holding the social asset
        that need to be disconnected."""

        Logger.normal('Restart the simulation.')

        social_assets_tokens = self.cycler.get_assets_tokens()
        report = self.cycler.match_report()
        self.cycler.restart(config_file, load_sim, write_sim)
        self.terminated = False
        self.actions_amount = 0
        self.actions_by_step.clear()
        self.actions_amount_by_step.clear()
        self.action_token_by_step.clear()

        return (*self.start(), report, social_assets_tokens)

    def do_step(self, token_action_list):
        """Do one step against the simulation.

        Do one step means that the simulation will process all the actions sent and activate the next step.

        :param token_action_list: The actions sent by each agent or social asset.
        :return tuple|None: If not terminated the first position holds the results from the actions sent and the second,
        the current step, else None."""

        Logger.normal(f'Process step {self.cycler.current_step}.')

        actions = [token_action_param['action'] for token_action_param in token_action_list]
        tokens = [token_action_param['token'] for token_action_param in token_action_list]

        self.actions_amount += len(token_action_list)
        self.actions_amount_by_step.append((self.cycler.current_step, len(token_action_list)))
        self.actions_by_step.append((self.cycler.current_step, actions))
        self.action_token_by_step.append((self.cycler.current_step, zip(tokens, actions)))

        if self.terminated:
            return None

        actions_results, requests = self.cycler.execute_actions(token_action_list)
        step = self.cycler.get_step()

        self.cycler.current_step += 1
        self.cycler.update_steps()

        if self.cycler.check_steps():
            self.terminated = True
            return actions_results, step, self.cycler.current_step, requests

        self.cycler.activate_step()

        return actions_results, step, self.cycler.current_step, requests

    def calculate_route(self, parameters):
        """Return the route calculated with the parameters given.

        :param parameters: Dict with the parameters to calculate the route.
        :return list: List containing the coordinate of the route or a String with a error."""

        return self.cycler.calculate_route(parameters)

    def get_map_percepts(self):
        """Get the constants information about the map.

        :return dict: constants attributes of the map in config file"""

        return self.cycler.get_map_percepts()

    def match_report(self):
        """Return a report of all agents from the current simulation match.

        :return dict: Dict with the token agents as key and your report as value."""

        return self.cycler.match_report()

    def simulation_report(self):
        """Return a report of all agents from all matchs.

        :return dict: Dict with the token agents as key and tour report as value."""

        return self.cycler.simulation_report()

    def log(self):
        """Save information about each step, the map, victims, flood, water samples, photos, every event related to the
        simulation.

        :return dict: Dictionary containing all the information that will be saved in a JSON file."""

        current_step = self.cycler.current_step
        max_steps = self.cycler.max_steps
        delivered_items = self.cycler.delivered_items
        agents_amount = len(self.cycler.agents_manager.get_info())
        agents = self.cycler.agents_manager.get_info()
        active_agents_amount = len(self.cycler.get_active_agents_info())
        active_agents = self.cycler.get_active_agents_info()
        assets_amount = len(self.cycler.social_assets_manager.get_info())
        assets = self.cycler.get_assets_info()
        active_assets_amount = len(self.cycler.get_active_assets_info())
        active_assets = self.cycler.get_active_assets_info()

        floods_amount = 0
        victims_in_events = 0
        victims_in_photo = 0
        victims_saved = 0
        victims_ignored = 0
        victims_dead_ignored = 0
        victims_dead_delivered = 0
        photos_taken = 0
        photos_analyzed = 0
        photos_ignored = 0
        water_samples_collected = 0
        water_samples_ignored = 0

        for i in range(current_step):
            if self.cycler.steps[i]['flood'] is None:
                continue

            floods_amount += 1
            victims_in_events += len(self.cycler.steps[i]['victims'])

            for victim in self.cycler.steps[i]['victims']:
                if not victim.active and victim.lifetime > 0:
                    victims_saved += 1

                elif not victim.active and victim.lifetime <= 0:
                    victims_dead_delivered += 1

                elif victim.lifetime <= 0:
                    victims_dead_ignored += 1

                else:
                    victims_ignored += 1

            for photo in self.cycler.steps[i]['photos']:
                if not photo.active:
                    photos_taken += 1

                victims_in_photo += len(photo.victims)

                if photo.analyzed:
                    photos_analyzed += 1

                    for victim in photo.victims:
                        if not victim.active and victim.lifetime > 0:
                            victims_saved += 1

                        elif not victim.active and victim.lifetime == 0:
                            victims_dead_delivered += 1

                        elif not victim.lifetime:
                            victims_dead_ignored += 1

                        victims_in_photo += 1

                else:
                    photos_ignored += 1

            for water_sample in self.cycler.steps[i]['water_samples']:
                if not water_sample.active:
                    water_samples_collected += 1

                else:
                    water_samples_ignored += 1

        # from .simulation_helpers.report import total_events, total_victims, total_photos, total_samples   
        from simulation_engine.simulation_helpers.report import Report   
        report = Report()  
            
        return {
            'environment': {
                'current_step': current_step,
                'max_steps': max_steps,
                'delivered_items': delivered_items,
                'floods_amount': report.total_events,
                'total_victims': report.victims.total,
                'victims_in_events': report.victims.known,
                'victims_in_photos': report.victims.hidden,
                'victims_rescued_alive': report.victims.alive,
                'victims_rescued_dead': report.victims.dead,
                'victims_dead_ignored': victims_dead_ignored,
                'victims_ignored': report.victims.ignored,
                'total_photos': report.photos.request,
                'photos_taken': report.photos.collected,
                'photos_analysed': report.photos.analysed,
                'photos_ignored': report.photos.ignored,
                'total_mud_samples': report.samples.request,
                'mud_samples_collected': report.samples.collected,
                'mud_samples_ignored': report.samples.ignored
            },
            'agents': {
                'active_agents_amount': active_agents_amount,
                'agents_amount': agents_amount,
                'active_agents': active_agents,
                'agents': agents,
            },
            'assets': {
                'active_assets_amount': active_assets_amount,
                'assets_amount': assets_amount,
                'active_assets': active_assets,
                'assets': assets
            },
            'actions': {
                'amount_of_actions_executed': self.actions_amount,
                'amount_of_actions_by_step': self.actions_amount_by_step,
                'actions_by_step': self.actions_by_step,
                'action_token_by_step': self.action_token_by_step
            },
        }
