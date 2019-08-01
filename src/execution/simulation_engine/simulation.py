from simulation_engine.simulation_helpers.cycle import Cycle


class Simulation:
    """Class that represents the engine of the simulation, connecting agents and social assets, doing steps and saving
    log information."""

    def __init__(self, config):
        self.cycler = Cycle(config)
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

    def connect_social_asset(self, token):
        """Connect the social asset to the simulation.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was connected else False."""

        return self.cycler.connect_social_asset(token)

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
        agents = self.cycler.get_active_agents_info()
        social_assets = self.cycler.get_active_assets_info()
        step = self.cycler.get_step()

        self.cycler.current_step += 1

        if self.cycler.check_steps():
            self.terminated = True
            return agents, social_assets, step

        self.cycler.activate_step()

        return agents, social_assets, step

    def restart(self, config_file):
        """Restart the simulation by regenerating all the simulation adn reseting all the log variables.

        :return tuple: First position holding the agents, second position the social assets and the third holding
        the current step."""

        self.cycler.restart(config_file)
        self.terminated = False
        self.actions_amount = 0
        self.actions_by_step.clear()
        self.actions_amount_by_step.clear()
        self.action_token_by_step.clear()

        return self.start()

    def do_step(self, token_action_list):
        """Do one step against the simulation.

        Do one step means that the simulation will process all the actions sent and activate the next step.

        :param token_action_list: The actions sent by each agent or social asset.
        :return tuple|None: If not terminated the first position holds the results from the actions sent and the second,
        the current step, else None."""

        actions = [token_action_param['action'] for token_action_param in token_action_list]
        tokens = [token_action_param['token'] for token_action_param in token_action_list]

        self.actions_amount += len(token_action_list)
        self.actions_amount_by_step.append((self.cycler.current_step, len(token_action_list)))
        self.actions_by_step.append((self.cycler.current_step, actions))
        self.action_token_by_step.append((self.cycler.current_step, zip(tokens, actions)))

        if self.terminated:
            return None

        actions_results = self.cycler.execute_actions(token_action_list)
        step = self.cycler.get_step()

        self.cycler.current_step += 1
        self.cycler.update_steps()

        if self.cycler.check_steps():
            self.terminated = True
            return actions_results, step

        self.cycler.activate_step()

        return actions_results, step

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
        victims_in_photo = 0
        victims_saved = 0
        victims_dead = 0
        photos_taken = 0
        photos_analyzed = 0
        photos_ignored = 0
        water_samples_collected = 0
        water_samples_ignored = 0

        for i in range(current_step):
            if not self.cycler.steps[i]['flood']:
                continue

            floods_amount += 1

            for victim in self.cycler.steps[i]['victims']:
                if not victim.active and victim.lifetime > 0:
                    victims_saved += 1

                elif not victim.lifetime:
                    victims_dead += 1

            for photo in self.cycler.steps[i]['photos']:
                if not photo.active:
                    photos_taken += 1

                victims_in_photo += len(photo.victims)

                if photo.analyzed:
                    photos_analyzed += 1

                    for victim in photo.victims:
                        if not victim.active and victim.lifetime > 0:
                            victims_saved += 1

                        elif not victim.lifetime:
                            victims_dead += 1

                        victims_in_photo += 1

                else:
                    photos_ignored += 1

            for water_sample in self.cycler.steps[i]['water_samples']:
                if not water_sample.active:
                    water_samples_collected += 1

                else:
                    water_samples_ignored += 1

        return {
            'environment': {
                'current_step': current_step,
                'max_steps': max_steps,
                'delivered_items': delivered_items,
                'floods_amount': floods_amount,
                'total_victims': self.cycler.max_victims,
                'total_victims_in_photos': victims_in_photo,
                'victims_saved': victims_saved,
                'victims_dead': victims_dead,
                'total_photos': self.cycler.max_photos,
                'photos_taken': photos_taken,
                'photos_analyzed': photos_analyzed,
                'photos_ignored': photos_ignored,
                'total_water_samples': self.cycler.max_water_samples,
                'water_samples_collected': water_samples_collected,
                'water_samples_ignored': water_samples_ignored
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
