from simulation_engine.exceptions.exceptions import *
from simulation_engine.simulation_helpers.map import Map
from simulation_engine.generator.generator import Generator
from simulation_engine.simulation_helpers.agents_manager import AgentsManager
from simulation_engine.simulation_helpers.social_assets_manager import SocialAssetsManager


class Cycle:
    def __init__(self, config):
        self.map = Map(config['map']['maps'][0], config['map']['proximity'])
        self.actions = config['actions']
        self.max_steps = config['map']['steps']
        generator = Generator(config, self.map)
        self.steps = generator.generate_events()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.cdm_location = (config['map']['centerLat'], config['map']['centerLon'])
        self.agents_manager = AgentsManager(config['agents'], self.cdm_location)
        self.social_assets_manager = SocialAssetsManager(config['map'], config['socialAssets'])

    def restart(self, config_file):
        self.map.restart(config_file['map']['maps'][0], config_file['map']['proximity'])
        generator = Generator(config_file, self.map)
        self.steps = generator.generate_events()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.max_steps = config_file['map']['steps']
        self.cdm_location = (config_file['map']['centerLat'], config_file['map']['centerLon'])
        self.agents_manager.restart(config_file['agents'], self.cdm_location)
        self.social_assets_manager.restart(config_file['map'], config_file['socialAssets'])

    def connect_agent(self, token):
        return self.agents_manager.connect(token)

    def connect_social_asset(self, token):
        return self.social_assets_manager.connect(token)

    def disconnect_agent(self, token):
        return self.agents_manager.disconnect(token)

    def disconnect_social_asset(self, token):
        return self.social_assets_manager.disconnect(token)

    def get_agents_info(self):
        return self.agents_manager.get_info()

    def get_active_agents_info(self):
        return self.agents_manager.get_active_info()

    def get_assets_info(self):
        return self.social_assets_manager.get_info()

    def get_active_assets_info(self):
        return self.social_assets_manager.get_active_info()

    def get_step(self):
        return self.steps[self.current_step]

    def get_previous_steps(self):
        previous_steps = []
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                previous_steps.append(self.steps[i])

        return previous_steps

    def activate_step(self):
        if self.steps[self.current_step]['flood'] is None:
            return

        self.steps[self.current_step]['flood'].active = True

        for victim in self.steps[self.current_step]['victims']:
            victim.active = True

        for water_sample in self.steps[self.current_step]['water_samples']:
            water_sample.active = True

        for photo in self.steps[self.current_step]['photos']:
            photo.active = True

    def check_steps(self):
        return self.current_step == self.max_steps

    def update_steps(self):
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                self.steps[i]['flood'].period -= 1

                if self.steps[i]['flood'].period == 0:
                    self.steps[i]['flood'].active = False

                    for victim in self.steps[i]['victims']:
                        victim.active = False

                    for water_sample in self.steps[i]['water_samples']:
                        water_sample.active = False

                    for photo in self.steps[i]['photos']:
                        photo.active = False

                        for victim in photo.victims:
                            victim.active = False

                else:
                    for victim in self.steps[i]['victims']:
                        if victim.lifetime <= 0:
                            victim.active = False
                        else:
                            victim.lifetime -= 1

                    for photo in self.steps[i]['photos']:
                        for victim in photo.victims:
                            if victim.lifetime <= 0:
                                victim.active = False
                            else:
                                victim.lifetime -= 1

    def execute_actions(self, token_action_dict):
        agents_tokens = self.agents_manager.get_tokens()
        assets_tokens = self.social_assets_manager.get_tokens()

        special_actions = ['carry', 'getCarried', 'deliverPhysical', 'deliverVirtual', 'receivePhysical',
                           'receiveVirtual']
        special_action_tokens = []

        action_results = []
        for token_action_param in token_action_dict:
            token, action, parameters = token_action_param.values()

            if action in special_actions:
                special_action_tokens.append([token, action, parameters])
                continue

            if token in agents_tokens:
                action_results.append(self._execute_agent_action(token, action, parameters))
                agents_tokens.remove(token)

            else:
                action_results.append(self._execute_asset_action(token, action, parameters))
                assets_tokens.remove(token)

        while special_action_tokens:
            token, action, param = special_action_tokens.pop(0)

            if token in agents_tokens:
                agents_tokens.remove(token)
                principal, secondary = self._execute_agent_special_action(token, action, param, special_action_tokens)

            else:
                assets_tokens.remove(token)
                principal, secondary = self._execute_asset_special_action(token, action, param, special_action_tokens)

            action_results.append(principal)

            if secondary is not None:
                if 'agent' in secondary:
                    agents_tokens.remove(secondary['agent'].token)
                else:
                    assets_tokens.remove(secondary['social_asset'].token)

                action_results.append(secondary)

        for token in agents_tokens:
            action_results.append(self._execute_agent_action(token, 'inactive', []))

        for token in assets_tokens:
            action_results.append(self._execute_asset_action(token, 'inactive', []))

        return action_results

    def _execute_agent_special_action(self, token, action_name, parameters, special_action_tokens):
        self.agents_manager.edit(token, 'last_action', action_name)
        self.agents_manager.edit(token, 'last_action_result', False)
        secondary_result = None

        if action_name not in self.actions:
            return {'agent': self.agents_manager.get(token), 'message': 'Wrong action name given.'}, secondary_result

        if not self.agents_manager.get(token).is_active:
            return {'agent': self.agents_manager.get(token), 'message': 'Agent is not active.'}, secondary_result

        if self.agents_manager.get(token).carried:
            return {'agent': self.agents_manager.get(token),
                    'message': 'Agent can not do any action while being carried.'}, secondary_result

        if not self._check_abilities_and_resources(token, action_name):
            return {'agent': self.agents_manager.get(token),
                    'message': 'Agent does not have the abilities or resources to complete the action.'}, secondary_result

        error_message = ''
        try:
            if action_name == 'carry':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'getCarried' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[0]) is not None:
                            self.agents_manager.add_physical(token, self.agents_manager.get(parameters[0]))
                            self.agents_manager.edit(token, 'last_action_result', True)
                            self.agents_manager.edit(parameters[0], 'carried', True)
                            self.agents_manager.edit(parameters[0], 'last_action', 'getCarried')
                            self.agents_manager.edit(parameters[0], 'last_action_result', True)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                        else:
                            self.agents_manager.add_physical(token,
                                                             self.social_assets_manager.get(parameters[0]))
                            self.agents_manager.edit(token, 'last_action_result', True)
                            self.social_assets_manager.edit(parameters[0], 'carried', True)
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'getCarried')
                            self.social_assets_manager.edit(parameters[0], 'last_action_result', True)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                    else:
                        raise FailedNoMatch('No other agent or social asset wants to be carried.')

                else:
                    raise FailedWrongParam('More or less than 1 parameter was given.')

            elif action_name == 'getCarried':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'carry' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[0]) is not None:
                            self.agents_manager.add_physical(parameters[0],
                                                             self.agents_manager.get(token))
                            self.agents_manager.edit(parameters[0], 'last_action_result', True)
                            self.agents_manager.edit(token, 'last_action_result', True)
                            self.agents_manager.edit(token, 'last_action', 'getCarried')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                        else:
                            self.social_assets_manager.add_physical(parameters[0],
                                                                    self.agents_manager.get(token))
                            self.social_assets_manager.edit(parameters[0], 'last_action_result', True)
                            self.agents_manager.edit(token, 'last_action_result', True)
                            self.agents_manager.edit(token, 'last_action', 'getCarried')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                    else:
                        raise FailedNoMatch('No other agent or social asset wants to carry.')

                else:
                    raise FailedWrongParam('More or less than 1 parameter was given.')

            elif action_name == 'deliverPhysical':
                if len(parameters) == 3:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[2] and sub_action == 'receivePhysical' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[2]) is not None:
                            self._deliver_physical_agent_agent(token, parameters)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[2]),
                                'message': ''
                            }

                        elif self.social_assets_manager.get(parameters[2]) is not None:
                            self._deliver_physical_agent_asset(token, parameters)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[2]),
                                'message': ''
                            }

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive physical items.')

                else:
                    self._deliver_physical_agent_cdm(token, parameters)

            elif action_name == 'deliverVirtual':
                if len(parameters) == 3:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[2] and sub_action == 'receiveVirtual' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[2]) is not None:
                            self._deliver_virtual_agent_agent(token, parameters)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[2]),
                                'message': ''
                            }

                        elif self.social_assets_manager.get(parameters[2]) is not None:
                            self._deliver_virtual_agent_asset(token, parameters)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[2]),
                                'message': ''
                            }

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

                else:
                    self._deliver_virtual_agent_cdm(token, parameters)

            elif action_name == 'receivePhysical':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 3:
                            if sub_token == parameters[0] and sub_action == 'deliverPhysical' and sub_param[2] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[0]) is not None:
                            self._deliver_physical_agent_agent(match[0], match[2])
                            self.agents_manager.edit(parameters[0], 'last_action', 'deliverPhysical')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }

                        elif self.social_assets_manager.get(parameters[0]) is not None:
                            self._deliver_physical_asset_agent(match[0], match[2])
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'deliverPhysical')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

                else:
                    raise FailedWrongParam('More than 1 parameter was given.')

            elif action_name == 'receiveVirtual':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 3:
                            if sub_token == parameters[0] and sub_action == 'deliverVirtual' and sub_param[2] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        special_action_tokens.remove(match)
                        if self.agents_manager.get(parameters[0]) is not None:
                            self._deliver_virtual_agent_agent(match[0], match[2])
                            self.agents_manager.edit(parameters[0], 'last_action', 'deliverVirtual')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }

                        elif self.social_assets_manager.get(parameters[0]) is not None:
                            self._deliver_virtual_asset_agent(match[0], match[2])
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'deliverVirtual')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

                else:
                    raise FailedWrongParam('More than 1 parameter was given.')

        except FailedCapacity as e:
            error_message = e.message

        except FailedLocation as e:
            error_message = e.message

        except FailedUnknownToken as e:
            error_message = e.message

        except FailedWrongParam as e:
            error_message = e.message

        except FailedNoMatch as e:
            error_message = e.message

        except FailedItemAmount as e:
            error_message = e.message

        except Exception as e:
            error_message = 'Unknown error: ' + str(e)

        finally:
            return {'agent': self.agents_manager.get(token), 'message': error_message}, secondary_result

    def _execute_asset_special_action(self, token, action_name, parameters, special_action_tokens):
        self.social_assets_manager.edit(token, 'last_action', action_name)
        self.social_assets_manager.edit(token, 'last_action_result', False)
        secondary_result = None

        if action_name not in self.actions:
            return {'social_asset': self.social_assets_manager.get(token),
                    'message': 'Wrong action name given.'}, secondary_result

        if not self.social_assets_manager.get(token).is_active:
            return {'social_asset': self.social_assets_manager.get(token),
                    'message': 'Social asset is not active.'}, secondary_result

        if self.social_assets_manager.get(token).carried:
            return {'social_asset': self.social_assets_manager.get(token),
                    'message': 'Social asset can not do any action while being carried.'}, secondary_result

        if action_name == 'pass':
            self.social_assets_manager.edit(token, 'last_action_result', True)
            return {'social_asset': self.social_assets_manager.get(token), 'message': ''}, secondary_result

        if not self._check_abilities_and_resources(token, action_name):
            return {'social_asset': self.social_assets_manager.get(token),
                    'message': 'Social asset does not have the abilities or resources to complete the action.'}, secondary_result

        error_message = ''
        try:
            if action_name == 'carry':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'getCarried' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[0]) is not None:
                            self.social_assets_manager.add_physical(token, self.agents_manager.get(parameters[0]))
                            self.social_assets_manager.edit(token, 'last_action_result', True)
                            self.agents_manager.edit(parameters[0], 'carried', True)
                            self.agents_manager.edit(parameters[0], 'last_action', 'getCarried')
                            self.agents_manager.edit(parameters[0], 'last_action_result', True)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)
                        else:
                            self.social_assets_manager.add_physical(token, self.social_assets_manager.get(parameters[0]))
                            self.social_assets_manager.edit(token, 'last_action_result', True)
                            self.social_assets_manager.edit(parameters[0], 'carried', True)
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'getCarried')
                            self.social_assets_manager.edit(parameters[0], 'last_action_result', True)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)
                    else:
                        raise FailedNoMatch('No other agent or social asset wants to be carried.')

                else:
                    raise FailedWrongParam('More or less than 1 parameter was given.')

            elif action_name == 'getCarried':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'carry' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[0]) is not None:
                            self.agents_manager.add_physical(parameters[0], self.agents_manager.get(token))
                            self.agents_manager.edit(parameters[0], 'last_action_result', True)
                            self.social_assets_manager.edit(token, 'last_action_result', True)
                            self.social_assets_manager.edit(token, 'last_action', 'getCarried')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)
                        else:
                            self.social_assets_manager.add_physical(parameters[0], self.agents_manager.get(token))
                            self.social_assets_manager.edit(parameters[0], 'last_action_result', True)
                            self.social_assets_manager.edit(token, 'last_action_result', True)
                            self.social_assets_manager.edit(token, 'last_action', 'getCarried')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)
                    else:
                        raise FailedNoMatch('No other agent or social asset wants to carry.')

                else:
                    raise FailedWrongParam('More or less than 1 parameter was given.')

            elif action_name == 'deliverPhysical':
                if len(parameters) == 3:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[2] and sub_action == 'receivePhysical' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[2]) is not None:
                            self._deliver_physical_asset_agent(token, parameters)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[2]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        elif self.social_assets_manager.get(parameters[2]) is not None:
                            self._deliver_physical_asset_asset(token, parameters)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[2]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive physical items.')

                else:
                    self._deliver_physical_asset_cdm(token, parameters)

            elif action_name == 'deliverVirtual':
                if len(parameters) == 3:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[2] and sub_action == 'receiveVirtual' and sub_param[0] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[2]) is not None:
                            self._deliver_virtual_asset_agent(token, parameters)
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[2]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        elif self.social_assets_manager.get(parameters[2]) is not None:
                            self._deliver_virtual_asset_asset(token, parameters)
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[2]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

                else:
                    self._deliver_virtual_asset_cdm(token, parameters)

            elif action_name == 'receivePhysical':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'deliverPhysical' and sub_param[2] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[0]) is not None:
                            self._deliver_physical_agent_asset(match[0], match[2])
                            self.agents_manager.edit(parameters[0], 'last_action', 'deliverPhysical')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        elif self.social_assets_manager.get(parameters[0]) is not None:
                            self._deliver_physical_asset_asset(match[0], match[2])
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'deliverPhysical')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

            elif action_name == 'receiveVirtual':
                if len(parameters) == 1:
                    match = None
                    for sub_token, sub_action, sub_param in special_action_tokens:
                        if len(sub_param) == 1:
                            if sub_token == parameters[0] and sub_action == 'deliverVirtual' and sub_param[2] == token:
                                match = [sub_token, sub_action, sub_param]
                                break

                    if match is not None:
                        if self.agents_manager.get(parameters[0]) is not None:
                            self._deliver_virtual_agent_asset(match[0], match[2])
                            self.agents_manager.edit(parameters[0], 'last_action', 'deliverVirtual')
                            secondary_result = {
                                'agent': self.agents_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        elif self.social_assets_manager.get(parameters[0]) is not None:
                            self._deliver_virtual_asset_asset(match[0], match[2])
                            self.social_assets_manager.edit(parameters[0], 'last_action', 'deliverVirtual')
                            secondary_result = {
                                'social_asset': self.social_assets_manager.get(parameters[0]),
                                'message': ''
                            }
                            special_action_tokens.remove(match)

                        else:
                            raise FailedUnknownToken('Given token was not found.')

                    else:
                        raise FailedNoMatch('No other agent or social asset wants to receive virtual items.')

        except FailedCapacity as e:
            error_message = e.message

        except FailedLocation as e:
            error_message = e.message

        except FailedUnknownToken as e:
            error_message = e.message

        except FailedWrongParam as e:
            error_message = e.message

        except FailedNoMatch as e:
            error_message = e.message

        except FailedInvalidKind as e:
            error_message = e.message

        except FailedItemAmount as e:
            error_message = e.message

        except Exception as e:
            error_message = 'Unknown error: ' + str(e)

        finally:
            return {'social_asset': self.social_assets_manager.get(token), 'message': error_message}, secondary_result

    def _deliver_physical_agent_cdm(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        agent = self.agents_manager.get(token)
        if self.map.check_location(agent.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0])

            else:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step
            })

            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _deliver_physical_agent_agent(self, token, parameters):
        delivering_agent = self.agents_manager.get(token)
        receiving_agent = self.agents_manager.get(parameters[2])
        if self.map.check_location(delivering_agent.location, receiving_agent.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_agent.physical_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The agent has no physical items of this kind to deliver.')

            if receiving_agent.physical_storage < amount * items[0].size:
                raise FailedCapacity('The receiving agent does not have enough physical storage.')

            removed_items = self.agents_manager.deliver_physical(delivering_agent.token, parameters[0], amount)
            for item in removed_items:
                self.agents_manager.add_physical(receiving_agent.token, item)

            self.agents_manager.edit(token, 'last_action_result', True)
            self.agents_manager.edit(receiving_agent.token, 'last_action', 'receivePhysical')
            self.agents_manager.edit(receiving_agent.token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located near the desired agent.')

    def _deliver_physical_agent_asset(self, token, parameters):
        delivering_agent = self.agents_manager.get(token)
        receiving_asset = self.social_assets_manager.get(parameters[2])
        if self.map.check_location(delivering_agent.location, receiving_asset.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_agent.physical_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The agent has no physical items of this kind to deliver.')

            if receiving_asset.physical_storage < amount * items[0].size:
                raise FailedCapacity('The receiving social asset does not have enough physical storage.')

            removed_items = self.agents_manager.deliver_physical(delivering_agent.token, parameters[0], amount)
            for item in removed_items:
                self.social_assets_manager.add_physical(receiving_asset.token, item)

            self.social_assets_manager.edit(receiving_asset.token, 'last_action', 'receivePhysical')
            self.social_assets_manager.edit(receiving_asset.token, 'last_action_result', True)
            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located near the desired social asset.')

    def _deliver_physical_asset_cdm(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        asset = self.social_assets_manager.get(token)
        if self.map.check_location(asset.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.social_assets_manager.deliver_physical(token, parameters[0])

            else:
                delivered_items = self.social_assets_manager.deliver_physical(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located at the CDM.')

    def _deliver_physical_asset_agent(self, token, parameters):
        delivering_asset = self.social_assets_manager.get(token)
        receiving_agent = self.agents_manager.get(parameters[2])
        if self.map.check_location(delivering_asset.location, receiving_agent.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_asset.physical_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The social asset has no physical items of this kind to deliver.')

            if receiving_agent.physical_storage < amount * items[0].size:
                raise FailedCapacity('The receiving agent does not have enough physical storage.')

            removed_items = self.social_assets_manager.deliver_physical(delivering_asset.token, parameters[0], amount)
            for item in removed_items:
                self.agents_manager.add_physical(receiving_agent.token, item)

            self.agents_manager.edit(receiving_agent.token, 'last_action', 'receivePhysical')
            self.agents_manager.edit(receiving_agent.token, 'last_action_result', True)
            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located near the desired agent.')

    def _deliver_physical_asset_asset(self, token, parameters):
        delivering_asset = self.social_assets_manager.get(token)
        receiving_asset = self.social_assets_manager.get(parameters[2])
        if self.map.check_location(delivering_asset.location, receiving_asset.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_asset.physical_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The social asset has no physical items of this kind to deliver.')

            if receiving_asset.physical_storage < amount * items[0].size:
                raise FailedCapacity('The receiving social asset does not have enough physical storage.')

            removed_items = self.social_assets_manager.deliver_physical(delivering_asset.token, parameters[0], amount)
            for item in removed_items:
                self.social_assets_manager.add_physical(receiving_asset.token, item)

            self.social_assets_manager.edit(receiving_asset.token, 'last_action', 'receivePhysical')
            self.social_assets_manager.edit(receiving_asset.token, 'last_action_result', True)
            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located near the desired social asset.')

    def _deliver_virtual_agent_cdm(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        agent = self.agents_manager.get(token)
        if self.map.check_location(agent.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.agents_manager.deliver_virtual(token, parameters[0])

            else:
                delivered_items = self.agents_manager.deliver_virtual(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _deliver_virtual_agent_agent(self, token, parameters):
        delivering_agent = self.agents_manager.get(token)
        receiving_agent = self.agents_manager.get(parameters[2])
        if self.map.check_location(delivering_agent.location, receiving_agent.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_agent.virtual_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The agent has no virtual items of this kind to deliver.')

            if receiving_agent.virtual_storage < amount * items[0].size:
                raise FailedCapacity('The receiving agent does not have enough virtual storage.')

            removed_items = self.agents_manager.deliver_virtual(delivering_agent.token, parameters[0], amount)
            for item in removed_items:
                self.agents_manager.add_virtual(receiving_agent.token, item)

            self.agents_manager.edit(receiving_agent.token, 'last_action', 'receiveVirtual')
            self.agents_manager.edit(receiving_agent.token, 'last_action_result', True)
            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located near the desired agent.')

    def _deliver_virtual_agent_asset(self, token, parameters):
        delivering_agent = self.agents_manager.get(token)
        receiving_asset = self.social_assets_manager.get(parameters[2])
        if self.map.check_location(delivering_agent.location, receiving_asset.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_agent.virtual_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The agent has no virtual items of this kind to deliver.')

            if receiving_asset.virtual_storage < amount * items[0].size:
                raise FailedCapacity('The receiving social asset does not have enough virtual storage.')

            removed_items = self.agents_manager.deliver_virtual(delivering_agent.token, parameters[0], amount)
            for item in removed_items:
                self.social_assets_manager.add_virtual(receiving_asset.token, item)

            self.social_assets_manager.edit(receiving_asset.token, 'last_action', 'receiveVirtual')
            self.social_assets_manager.edit(receiving_asset.token, 'last_action_result', True)
            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located near the desired agent.')

    def _deliver_virtual_asset_cdm(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        asset = self.social_assets_manager.get(token)
        if self.map.check_location(asset.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.social_assets_manager.deliver_virtual(token, parameters[0])

            else:
                delivered_items = self.social_assets_manager.deliver_virtual(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located at the CDM.')

    def _deliver_virtual_asset_agent(self, token, parameters):
        delivering_asset = self.social_assets_manager.get(token)
        receiving_agent = self.agents_manager.get(parameters[2])
        if self.map.check_location(delivering_asset.location, receiving_agent.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_asset.virtual_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The social asset has no virtual items of this kind to deliver.')

            if receiving_agent.virtual_storage < amount * items[0].size:
                raise FailedCapacity('The receiving agent does not have enough virtual storage.')

            removed_items = self.social_assets_manager.deliver_virtual(delivering_asset.token, parameters[0], amount)
            for item in removed_items:
                self.agents_manager.add_virtual(receiving_agent.token, item)

            self.agents_manager.edit(receiving_agent.token, 'last_action', 'receiveVirtual')
            self.agents_manager.edit(receiving_agent.token, 'last_action_result', True)
            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located near the desired agent.')

    def _deliver_virtual_asset_asset(self, token, parameters):
        delivering_asset = self.social_assets_manager.get(token)
        receiving_asset = self.social_assets_manager.get(parameters[2])
        if self.map.check_location(delivering_asset.location, receiving_asset.location):
            amount = 0 if parameters[1] < 0 else parameters[1]

            items = [item for item in delivering_asset.virtual_storage_vector if item.type == parameters[0]]
            if not items:
                raise FailedItemAmount('The social asset has no virtual items of this kind to deliver.')

            if receiving_asset.virtual_storage < amount * items[0].size:
                raise FailedCapacity('The receiving social asset does not have enough virtual storage.')

            removed_items = self.social_assets_manager.deliver_virtual(delivering_asset.token, parameters[0], amount)
            for item in removed_items:
                self.social_assets_manager.add_virtual(receiving_asset.token, item)

            self.social_assets_manager.edit(receiving_asset.token, 'last_action', 'receiveVirtual')
            self.social_assets_manager.edit(receiving_asset.token, 'last_action_result', True)
            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The social asset is not located near the desired agent.')

    def _execute_agent_action(self, token, action_name, parameters):
        self.agents_manager.edit(token, 'last_action', action_name)
        self.agents_manager.edit(token, 'last_action_result', False)

        if action_name == 'inactive':
            self.agents_manager.edit(token, 'last_action', 'pass')
            return {'agent': self.agents_manager.get(token), 'message': 'Agent did not send any action.'}

        if action_name not in self.actions:
            return {'agent': self.agents_manager.get(token), 'message': 'Wrong action name given.'}

        if not self.agents_manager.get(token).is_active:
            return {'agent': self.agents_manager.get(token), 'message': 'Agent is not active.'}

        if self.agents_manager.get(token).carried:
            return {
                'agent': self.agents_manager.get(token),
                'message': 'Agent can not do any action while being carried.'}

        if action_name == 'pass':
            self.agents_manager.edit(token, 'last_action_result', True)
            return {'agent': self.agents_manager.get(token), 'message': ''}

        if not self._check_abilities_and_resources(token, action_name):
            return {
                'agent': self.agents_manager.get(token),
                'message': 'Agent does not have the abilities or resources to complete the action.'}

        error_message = ''
        try:
            if action_name == 'charge':
                self._charge_agent(token, parameters)

            elif action_name == 'move':
                self._move_agent(token, parameters)

            elif action_name == 'rescueVictim':
                self._rescue_victim_agent(token, parameters)

            elif action_name == 'collectWater':
                self._collect_water_agent(token, parameters)

            elif action_name == 'takePhoto':
                self._take_photo_agent(token, parameters)

            elif action_name == 'analyzePhoto':
                self._analyze_photo_agent(token, parameters)

            elif action_name == 'searchSocialAsset':
                self._search_social_asset_agent(token, parameters)

        except FailedNoSocialAsset as e:
            error_message = e.message

        except FailedWrongParam as e:
            error_message = e.message

        except FailedNoRoute as e:
            error_message = e.message

        except FailedInsufficientBattery as e:
            error_message = e.message

        except FailedCapacity as e:
            error_message = e.message

        except FailedInvalidKind as e:
            error_message = e.message

        except FailedItemAmount as e:
            error_message = e.message

        except FailedLocation as e:
            error_message = e.message

        except FailedUnknownFacility as e:
            error_message = e.message

        except FailedUnknownItem as e:
            error_message = e.message

        except Exception as e:
            error_message = 'Unknown error: ' + str(e)

        finally:
            return {'agent': self.agents_manager.get(token), 'message': error_message}

    def _execute_asset_action(self, token, action_name, parameters):
        self.social_assets_manager.edit(token, 'last_action', action_name)
        self.social_assets_manager.edit(token, 'last_action_result', False)

        if action_name == 'inactive':
            self.social_assets_manager.edit(token, 'last_action', 'pass')
            return {
                'social_asset': self.social_assets_manager.get(token),
                'message': 'Social asset did not send any action.'}

        if action_name not in self.actions:
            return {
                'social_asset': self.social_assets_manager.get(token),
                'message': 'Wrong action name given.'}

        if not self.social_assets_manager.get(token).is_active:
            return {
                'social_asset': self.social_assets_manager.get(token),
                'message': 'Social asset is not active.'}

        if self.social_assets_manager.get(token).carried:
            return {
                'social_asset': self.social_assets_manager.get(token),
                'message': 'Social asset can not do any action while being carried.'}

        if action_name == 'pass':
            self.social_assets_manager.edit(token, 'last_action_result', True)
            return {'social_asset': self.social_assets_manager.get(token), 'message': ''}

        if not self._check_abilities_and_resources(token, action_name):
            return {
                'social_asset': self.social_assets_manager.get(token),
                'message': 'Social asset does not have the abilities or resources to complete the action.'}

        error_message = ''
        try:
            if action_name == 'move':
                self._move_asset(token, parameters)

            elif action_name == 'rescueVictim':
                self._rescue_victim_asset(token, parameters)

            elif action_name == 'collectWater':
                self._collect_water_asset(token, parameters)

            elif action_name == 'takePhoto':
                self._take_photo_asset(token, parameters)

            elif action_name == 'analyzePhoto':
                self._analyze_photo_asset(token, parameters)

            elif action_name == 'searchSocialAsset':
                self._search_social_asset_asset(token, parameters)

        except FailedNoSocialAsset as e:
            error_message = e.message

        except FailedWrongParam as e:
            error_message = e.message

        except FailedNoRoute as e:
            error_message = e.message

        except FailedInsufficientBattery as e:
            error_message = e.message

        except FailedCapacity as e:
            error_message = e.message

        except FailedInvalidKind as e:
            error_message = e.message

        except FailedItemAmount as e:
            error_message = e.message

        except FailedLocation as e:
            error_message = e.message

        except FailedUnknownFacility as e:
            error_message = e.message

        except FailedUnknownItem as e:
            error_message = e.message

        except UnableToReach as e:
            error_message = e.message

        except Exception as e:
            error_message = 'Unknown error: ' + str(e)

        finally:
            return {'social_asset': self.social_assets_manager.get(token), 'message': error_message}

    def _check_abilities_and_resources(self, token, action):
        if self.agents_manager.get(token) is None:
            actor = self.social_assets_manager.get(token)
        else:
            actor = self.agents_manager.get(token)

        if actor is None:
            exit('Internal error. Non registered token requested.')

        for ability in self.actions[action]['abilities']:
            if ability not in actor.abilities:
                return False

        for resource in self.actions[action]['resources']:
            if resource not in actor.resources:
                return False

        return True

    def _charge_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        if self.map.check_location(self.agents_manager.get(token).location, self.cdm_location):
            self.agents_manager.charge(token)
            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _move_agent(self, token, parameters):
        if len(parameters) == 1:
            if parameters[0] == 'cdm':
                destination = self.cdm_location
            else:
                raise FailedUnknownFacility('Unknown facility.')

        elif len(parameters) <= 0:
            raise FailedWrongParam('Less than 1 parameter was given.')

        elif len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        else:
            destination = parameters

        agent = self.agents_manager.get(token)

        if not agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')

        elif self.map.check_location(agent.location, destination):
            self.agents_manager.edit(token, 'route', [])
            self.agents_manager.edit(token, 'destination_distance', 0)
            self.agents_manager.edit(token, 'last_action_result', True)

        else:
            if not agent.route or destination != agent.route[-1]:
                nodes = []
                for i in range(self.current_step):
                    if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                        nodes.extend(self.steps[i]['flood'].list_of_nodes)

                result, route, distance = self.map.get_route(agent.location, destination, agent.role, agent.speed,
                                                             nodes)

                if not result:
                    self.agents_manager.edit(token, 'route', [])
                    self.agents_manager.edit(token, 'destination_distance', 0)

                    raise UnableToReach('Agent is not capable of entering flood locations.')

                else:
                    self.agents_manager.edit(token, 'route', route)
                    self.agents_manager.edit(token, 'destination_distance', distance)

            if self.agents_manager.get(token).destination_distance:
                self.agents_manager.update_location(token)
                distance = self.map.node_distance(self.map.get_closest_node(*agent.location),
                                                  self.map.get_closest_node(*destination))
                self.agents_manager.edit(token, 'destination_distance', distance)
                self.agents_manager.edit(token, 'last_action_result', True)
                self.agents_manager.discharge(token)

    def _move_asset(self, token, parameters):
        if len(parameters) == 1:
            if parameters[0] == 'cdm':
                destination = self.cdm_location
            else:
                raise FailedUnknownFacility('Unknown facility.')

        elif len(parameters) <= 0:
            raise FailedWrongParam('Less than 1 parameter was given.')

        elif len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        else:
            destination = parameters

        asset = self.social_assets_manager.get(token)

        if self.map.check_location(asset.location, destination):
            self.social_assets_manager.edit(token, 'route', [])
            self.social_assets_manager.edit(token, 'destination_distance', 0)
            self.social_assets_manager.edit(token, 'last_action_result', True)

        else:
            if not asset.route:
                nodes = []
                for i in range(self.current_step):
                    if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                        nodes.extend(self.steps[i]['flood'].list_of_nodes)

                result, route, distance = self.map.get_route(asset.location, destination, 'car', asset.speed, nodes)

                if not result:
                    self.social_assets_manager.edit(token, 'route', [])
                    self.social_assets_manager.edit(token, 'destination_distance', 0)

                    raise UnableToReach('Asset is not capable of entering flood locations.')

                else:
                    self.social_assets_manager.edit(token, 'route', route)
                    self.social_assets_manager.edit(token, 'destination_distance', distance)

            if self.social_assets_manager.get(token).destination_distance:
                self.social_assets_manager.update_location(token)
                _, _, distance = self.map.get_route(asset.location, destination, 'car', asset.speed, [])
                self.social_assets_manager.edit(token, 'destination_distance', distance)
                self.social_assets_manager.edit(token, 'last_action_result', True)

    def _rescue_victim_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get(token)

        for i in range(self.current_step):
            for victim in self.steps[i]['victims']:
                if victim.active and self.map.check_location(victim.location, agent.location):
                    victim.active = False
                    self.agents_manager.add_physical(token, victim)
                    self.agents_manager.edit(token, 'last_action_result', True)
                    return

            for photo in self.steps[i]['photos']:
                for victim in photo.victims:
                    if victim.active and self.map.check_location(victim.location, agent.location):
                        victim.active = False
                        self.agents_manager.add_physical(token, victim)
                        self.agents_manager.edit(token, 'last_action_result', True)
                        return

        raise FailedUnknownItem('No victim by the given location is known.')

    def _rescue_victim_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get(token)

        for i in range(self.current_step):
            for victim in self.steps[i]['victims']:
                if victim.active and self.map.check_location(victim.location, asset.location):
                    victim.active = False
                    self.social_assets_manager.add_physical(token, victim)
                    self.social_assets_manager.edit(token, 'last_action_result', True)
                    return

            for photo in self.steps[i]['photos']:
                for victim in photo.victims:
                    if victim.active and self.map.check_location(victim.location, asset.location):
                        victim.active = False
                        self.social_assets_manager.add_physical(token, victim)
                        self.social_assets_manager.edit(token, 'last_action_result', True)
                        return

        raise FailedUnknownItem('No victim by the given location is known.')

    def _collect_water_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get(token)
        for i in range(self.current_step):
            for water_sample in self.steps[i]['water_samples']:
                if water_sample.active and self.map.check_location(water_sample.location, agent.location):
                    water_sample.active = False
                    self.agents_manager.add_physical(token, water_sample)
                    self.agents_manager.edit(token, 'last_action_result', True)
                    return

        raise FailedLocation('The agent is not in a location with a water sample event.')

    def _collect_water_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get(token)
        for i in range(self.current_step):
            for water_sample in self.steps[i]['water_samples']:
                if water_sample.active and self.map.check_location(water_sample.location, asset.location):
                    water_sample.active = False
                    self.social_assets_manager.add_physical(token, water_sample)
                    self.social_assets_manager.edit(token, 'last_action_result', True)
                    return

        raise FailedLocation('The asset is not in a location with a water sample event.')

    def _take_photo_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get(token)
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.active and self.map.check_location(photo.location, agent.location):
                    photo.active = False
                    self.agents_manager.add_virtual(token, photo)
                    self.agents_manager.edit(token, 'last_action_result', True)
                    return

        raise FailedLocation('The agent is not in a location with a photograph event.')

    def _take_photo_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get(token)
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.active and self.map.check_location(photo.location, asset.location):
                    photo.active = False
                    self.social_assets_manager.add_virtual(token, photo)
                    self.social_assets_manager.edit(token, 'last_action_result', True)
                    return

        raise FailedLocation('The asset is not in a location with a photograph event.')

    def _analyze_photo_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get(token)
        if len(agent.virtual_storage_vector) == 0:
            raise FailedItemAmount('The agent has no photos to analyze.')

        photo_identifiers = []
        victim_identifiers = []
        for photo in agent.virtual_storage_vector:
            for victim in photo.victims:
                victim_identifiers.append(victim.identifier)

            photo_identifiers.append(photo.identifier)

        self._update_photos_state(photo_identifiers)
        self.agents_manager.edit(token, 'last_action_result', True)
        self.agents_manager.clear_virtual_storage(token)

    def _analyze_photo_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get(token)
        if len(asset.virtual_storage_vector) == 0:
            raise FailedItemAmount('The asset has no photos to analyze.')

        photo_identifiers = []
        victim_identifiers = []
        for photo in asset.virtual_storage_vector:
            for victim in photo.victims:
                victim_identifiers.append(victim.identifier)

            photo_identifiers.append(photo.identifier)

        self._update_photos_state(photo_identifiers)
        self.social_assets_manager.edit(token, 'last_action_result', True)
        self.social_assets_manager.clear_virtual_storage(token)

    def _search_social_asset_agent(self, token, parameters):
        if not self.social_assets_manager.get_tokens():
            raise FailedNoSocialAsset('No social asset connected.')

        if len(parameters) != 1:
            raise FailedWrongParam('Wrong amount of parameters given.')

        closer_asset = None
        distance = 999999
        for asset_token in self.social_assets_manager.get_tokens():
            asset = self.social_assets_manager.get(asset_token)
            if asset.is_active:
                if parameters[0] == asset.profession:
                    current_dist = self.map.euclidean_distance(self.agents_manager.get(token).location,
                                                               asset.location)
                    if current_dist <= distance:
                        distance = current_dist
                        closer_asset = asset

        if closer_asset is None:
            raise FailedNoSocialAsset('No social asset found for the needed purposes.')

        else:
            self.agents_manager.add(token, closer_asset)
            self.agents_manager.edit(token, 'last_action_result', True)

    def _search_social_asset_asset(self, token, parameters):
        if not self.social_assets_manager.get_tokens():
            raise FailedNoSocialAsset('No social asset connected.')

        if len(parameters) != 1:
            raise FailedWrongParam('Wrong amount of parameters given.')

        closer_asset = None
        distance = 999999
        for asset_token in self.social_assets_manager.get_tokens():
            asset = self.social_assets_manager.get(asset_token)
            if asset.is_active:
                if parameters[0] == asset.profession and token != asset.token:
                    current_dist = self.map.euclidean_distance(self.social_assets_manager.get(token).location, asset.location)
                    if current_dist <= distance:
                        distance = current_dist
                        closer_asset = asset

        if closer_asset is None:
            raise FailedNoSocialAsset('No social asset found for the needed purposes.')

        else:
            self.social_assets_manager.add(token, closer_asset)
            self.social_assets_manager.edit(token, 'last_action_result', True)

    def _update_photos_state(self, identifiers):
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.identifier in identifiers:
                    identifiers.remove(photo.identifier)
                    photo.analyzed = True
                    for victim in photo.victims:
                        victim.active = True
