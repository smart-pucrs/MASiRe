import os
import re
import json
import pathlib
import traceback
from simulation_engine.copycat import CopyCat
from simulation_engine.simulation_helpers.logger import Logger
import logging

logger = logging.getLogger(__name__)

class JsonFormatter:
    """Class that converts all the objects into JSON style dicts."""

    def __init__(self, config, load_sim, write_sim):
        self.logger = logging.getLogger(__name__) 
        config_location = pathlib.Path(__file__).parents[3] / config
        self.copycat = CopyCat(json.load(open(config_location, 'r')), load_sim, write_sim)

    def log(self):
        """Do the log and returns a JSON response.

        :return dict: Dictionary with status (0|1) if it is possible do to another round and the appropriate message."""
        if not self.copycat.log():
            return {'status': 0, 'message': 'No more maps available for matches.'}
        else:
            return {'status': 1, 'message': 'New match generated.'}

    def restart(self):
        """Restart the simulation and returns a JSON response.

        All the agents, social assets and events are converted, the copycat class prevents from the formatter changing
        the objects inside the engine.

        :return dict: Dictionary with status representing if any errors were found, the list of agents and social assets,
        the event with the flood, victims, photos and water samples and a general message."""

        Logger.normal('Try to restart the simulation.')

        try:
            agents, step, current_step, new_map_percepts, report, assets_tokens = self.copycat.restart()
            message = 'Simulation restarted.'

            json_agents_init = [{'agent': self.jsonify_agent(agent)} for agent in agents]

            json_agents = self.jsonify_agents(agents)
            json_actors = [{'agent': agent, 'message': message} for agent in json_agents]
            environment = {'events': self.jsonify_events(step), 'step': current_step}

            percepts = {'status': 1, 'actors': json_actors, 'environment': environment, 'message': 'Simulation restarted.'}
            initial_percepts = {'status': 1, 'agents': json_agents_init, 'map_percepts': new_map_percepts, 'message': ''}
            report_response = {'status': 1, 'report': report, 'message': ''}

            Logger.normal('Simulation restarted.')

            return {'status': 1, 'initial_percepts': initial_percepts, 'assets_tokens': assets_tokens,
                    'report': report_response, 'percepts': percepts, 'message': message}

        except Exception as e:
            logger.critical(e,exc_info=True)
            Logger.critical(f'Error to restart the simulation, Error: {str(e)}.')

            return {'status': 0, 'message': f'An error occurred during restart: "{str(e)}"'}

    def connect_agent(self, token):
        """Connect the agent to the simulation and returns a JSON response.

        :param token: The generated token for the agent.
        :return dict: Dictionary with status representing if any errors were found and a general message."""
        Logger.normal('Try to connect a agent.')

        response = {'status': 0, 'message': ''}

        try:
            initial_percepts = self.copycat.connect_agent(token)

            if initial_percepts:
                response['agents'] = [{'agent': self.jsonify_agent(initial_percepts['agent_percepts'])}]
                response['map_percepts'] = initial_percepts['map_percepts']
                response['status'] = 1
                response['message'] = 'Agent connected.'

                Logger.normal('Agent connected.')

                return response
            else:
                response['message'] = 'Agent could not connect.'

                Logger.error('Agent could not connect.')

                return response
        except Exception as e:
            response['message'] = f'An error occurred during connection: {str(e)}.'
            Logger.error(f'Unknown error: {str(e)}.')

            return response

    def connect_social_asset(self, main_token, token):
        """Connect the social asset to the simulation and returns a JSON response.

        :param main_token: Agent token that request the social asset connection.
        :param token: The generated token for the social asset.
        :return dict: Dictionary with status representing if any errors were found, the social asset object and a
        general message."""
        Logger.normal('Try to connect a social asset.')

        response = {'status': 0, 'message': ''}

        try:
            initial_percepts = self.copycat.connect_social_asset(main_token, token)

            if response:
                response['agents'] = [{'asset': self.jsonify_asset(initial_percepts['agent_percepts'])}]
                response['map_percepts'] = initial_percepts['map_percepts']
                response['status'] = 1
                response['message'] = 'Social asset connected.'

                Logger.normal('Social asset connected.')

                return response
            else:
                response['message'] = 'Social asset could not connect.'

                Logger.normal('Social asset could not connect.')

                return response
        except Exception as e:
            response['message'] = f'An error occurred during connection: {str(e)}.'

            Logger.error(f'Unknown error: {str(e)}.')

            return response

    def match_report(self):
        Logger.normal('Generate match report.')
        response = {'status': 0, 'message': ''}
        report = {'status': 0, 'message': ''}

        try:
            match_report = self.copycat.match_report()

            report['status'] = 1
            report['report'] = match_report

            response['report'] = report

        except Exception as e:
            response['message'] = str(e)
            report['message'] = str(e)

            response['report'] = report

        return response

    def simulation_report(self):
        Logger.normal('Generate simulation report.')
        response = {'status': 0, 'message': ''}

        try:
            report = self.copycat.simulation_report()

            if isinstance(report, str):
                Logger.error('Error to generate simulation report.')
                response['message'] = 'Error to generate simulation report.'
            
            else:
                response['status'] = 1
                response['report'] = report

        except Exception as e:
            response['message'] = str(e)

        return response

    def finish_social_asset_connections(self, tokens):
        Logger.normal('Finishing social assets connections.')

        try:
            response = self.copycat.finish_social_asset_connections(tokens)
            json_actors = []
            if response is not None:
                for agent in response:
                    json_actors.append({'asset': self.jsonify_asset(agent), 'message': 'Social asset connected'})

            Logger.normal('Social assets connection finished.')

            return {'status': 1, 'actors': json_actors, 'message': 'Finish social asset connections'}

        except Exception as e:
            Logger.error(f'Unknown error {str(e)}.')

            return {'status': 0, 'message': f'An error occurred during connection: {str(e)}.'}

    def disconnect_agent(self, token):
        """Disconnect the agent to the simulation and returns a JSON response.

        :param token: The generated token for the agent.
        :return dict: Dictionary with status representing if any errors were found and a general message."""

        Logger.normal('Try to disconnect a agent.')

        try:
            response = self.copycat.disconnect_agent(token)

            if response:
                Logger.normal('Agent disconnected.')

                return {'status': 1, 'message': 'Agent disconnected.'}

            else:
                Logger.normal('Agent is not connected.')

                return {'status': 0, 'message': 'Agent is not connected.'}

        except Exception as e:
            Logger.error(f'Unknown error: {str(e)}.')

            return {'status': 0, 'message': f'An error occurred during disconnection: {str(e)}.'}

    def disconnect_social_asset(self, token):
        """Disconnect the social asset to the simulation and returns a JSON response.

        :param token: The generated token for the social asset.
        :return dict: Dictionary with status representing if any errors were found and a general message."""

        Logger.normal('Try to disconnect a social asset.')

        try:
            response = self.copycat.disconnect_social_asset(token)

            if response:
                Logger.normal('Social asset disconnected.')

                return {'status': 1, 'message': 'Social asset disconnected.'}

            else:
                Logger.normal('Social asset is not connected.')

                return {'status': 0, 'message': 'Social asset is not connected.'}

        except Exception as e:
            Logger.error(f'Unknown error: {str(e)}.')

            return {'status': 0, 'message': f'An error occurred during disconnection: {str(e)}.'}

    def start(self):
        """Start the simulation and returns a JSON response.

        All the agents, social assets and events are converted, the copycat class prevents from the formatter changing
        the objects inside the engine.

        :return dict: Dictionary with status representing if any errors were found, the list of agents and social assets,
        the event with the flood, victims, photos and water samples and a general message."""

        logger.info('Try to start the simulation.')

        try:
            response = self.copycat.start()
            message = 'Simulation started.'

            json_agents = self.jsonify_agents(response[0])
            json_actors = [{'agent': agent, 'message': message} for agent in [*json_agents]]
            environment = {'events': self.jsonify_events(response[1]), 'step': response[2]}
            map_percepts = response[3]

            Logger.normal(message)

            return {'status': 1, 'actors': json_actors, 'environment': environment,
                    'map_percepts': map_percepts, 'message': message}

        except Exception as e:
            logger.error(e,exc_info=True)

            return {'status': 0, 'message': f'An error occurred during restart: "{str(e)}"'}

    def calculate_route(self, parameters):
        """Return the route calculated with the parameters given.

        :param parameters: list with the parameters to calculate the route.
        :return dict: Dictionary with the result of the operation, the route calculated, the distance od the route and
        a message."""

        Logger.normal('Route Calculator Service called.')

        try:
            response = self.copycat.calculate_route(parameters)
            response['route'] = [self.format_location(coord) for coord in response['route']]

            return {'status': 1, 'response': response}

        except Exception as e:
            return {'status': 0, 'message': f'Unknown Error: {str(e)}'}

    def do_step(self, token_action_list):
        """Do a step on the simulation.

        After the step, all the results from the actions are converted to JSON.

        :param token_action_list: List with all the tokens combined with the action|parameter sent.
        :return dict: Dictionary with a status representing if any errors were found, the list of agents and social
        assets, the event with the flood, victims, photos, and water samples and a general message."""

        Logger.normal('Try to process the current step.')

        try:
            Logger.normal('Process the agents actions.')
            response = self.copycat.do_step(token_action_list)

            if response is None:
                return {'status': 1, 'message': 'Simulation finished.'}

            json_actors = []
            for obj in response[0]:
                if 'agent' in obj:
                    json_actors.append({'agent': self.jsonify_agent(obj['agent']), 'message': obj['message']})
                else:
                    json_actors.append({'asset': self.jsonify_asset(obj['social_asset']), 'message': obj['message']})

            json_events = self.jsonify_events(response[1])
            environment = {'events': json_events, 'step': response[2]}

            if response[3]:
                Logger.normal('A social asset request connection will start.')

                messages = {'environment': environment, 'actors': json_actors}
                current_step = response[2] - 1

                return {'status': 2, 'requests': response[3], 'messages': messages,
                        'current_step': current_step, 'message': 'Step completed.'}

            Logger.normal('Step processed.')

            return {'status': 1, 'actors': json_actors, 'environment': environment, 'message': 'Step completed.'}

        except Exception as e:            
            logger.error(e,exc_info=True)
            return {'status': 0, 'message': f'An error occurred during step: "{str(e)}"'}

    def save_logs(self):
        """Write all the saved logs to a file on the root of the project, the file will be inside a folder structure
        based on the date and time the simulation ran."""

        Logger.normal('Save the logs.')

        year, month, day, hour, minute, config_file, logs = self.copycat.get_logs()
        path = pathlib.Path(__file__).parents[3] / str(year) / str(month) / str(day) / str(config_file)

        os.makedirs(str(path.absolute()), exist_ok=True)

        hour = '{:0>2d}'.format(hour)
        minute = '{:0>2d}'.format(minute)

        for log in logs:
            delivered_items = []
            for item_log in logs[log]['environment']['delivered_items']:
                delivered_items.extend(item_log['items'])
            json_items = self.jsonify_delivered_items(delivered_items)

            json_agents = self.jsonify_agents(logs[log]['agents']['agents'])
            json_assets = self.jsonify_assets(logs[log]['assets']['assets'])
            json_active_agents = self.jsonify_agents(logs[log]['agents']['active_agents'])
            json_active_assets = self.jsonify_assets(logs[log]['assets']['active_assets'])
            json_action_token_by_step = self.jsonify_action_token_by_step(logs[log]['actions']['action_token_by_step'])
            json_acts_by_step = self.jsonify_amount_of_actions_by_step(logs[log]['actions']['amount_of_actions_by_step'])
            json_actions_by_step = self.jsonify_actions_by_step(logs[log]['actions']['actions_by_step'])

            logs[log]['environment']['delivered_items'] = json_items
            logs[log]['agents']['agents'] = json_agents
            logs[log]['assets']['assets'] = json_assets
            logs[log]['agents']['active_agents'] = json_active_agents
            logs[log]['assets']['active_assets'] = json_active_assets
            logs[log]['actions']['action_token_by_step'] = json_action_token_by_step
            logs[log]['actions']['amount_of_actions_by_step'] = json_acts_by_step
            logs[log]['actions']['actions_by_step'] = json_actions_by_step

            map_log = re.sub('([\w\s\d]+?\\\\)|([\w\s\d]+?/)|(\.\w+)', '', log)

            with open(str((path / f'LOG FILE {map_log} at {hour}h {minute}min.txt').absolute()), 'w') as file:
                file.write(json.dumps(logs[log], sort_keys=False, indent=4))
                file.write('\n\n' + '=' * 120 + '\n\n')

    def jsonify_agents(self, agents_list):
        """Transform a list of agents objects into JSON objects.

        :param agents_list: List of the agents objects.
        :return list: List of all the agents as JSON objects."""

        json_agents = []
        for agent in agents_list:
            json_agents.append(self.jsonify_agent(agent))

        return json_agents

    def jsonify_assets(self, assets_list):
        """Transform a list of social assets objects into JSON objects.

        :param assets_list: List of the social assets objects.
        :return list: List of all the social assets as JSON objects."""

        json_assets = []
        for asset in assets_list:
            json_assets.append(self.jsonify_asset(asset))

        return json_assets

    def jsonify_agent(self, agent):
        """Transform a single agent variables into a JSON object.

        The keys of the dict were organized from priority and relation to make easier for the user to read it.

        :param agent: The agent object saved in the simulation.
        :return dict: Dictionary with all the information from the agent."""

        json_physical_items = self.jsonify_delivered_items(agent.physical_storage_vector)

        json_virtual_items = self.jsonify_delivered_items(agent.virtual_storage_vector)

        json_route = [self.format_location(location) for location in agent.route]

        json_social_assets = self.jsonify_social_assets(agent.social_assets)

        return {
            'token': agent.token,
            'type': agent.type,
            'active': agent.is_active,
            'carried': agent.carried,
            'role': agent.role,
            'size': agent.min_size,
            'abilities': agent.abilities,
            'resources': agent.resources,
            'max_charge': agent.max_charge,
            'speed': agent.speed,
            'physical_capacity': agent.physical_capacity,
            'virtual_capacity': agent.virtual_capacity,
            'last_action': agent.last_action,
            'last_action_result': agent.last_action_result,
            'location': self.format_location(agent.location),
            'route': json_route,
            'destination_distance': agent.destination_distance,
            'battery': agent.actual_battery,
            'physical_storage': agent.physical_storage,
            'physical_storage_vector': json_physical_items,
            'virtual_storage': agent.virtual_storage,
            'virtual_storage_vector': json_virtual_items,
            'social_assets': json_social_assets
        }

    def jsonify_asset(self, asset):
        """Transform a single social asset variables into a JSON object.

        The keys of the dict were organized from priority and relation to make easier for the user to read it.

        :param asset: The social asset object saved in the simulation.
        :return dict: Dictionary with all the information from the social asset."""

        json_physical_items = self.jsonify_delivered_items(asset.physical_storage_vector)

        json_virtual_items = self.jsonify_delivered_items(asset.virtual_storage_vector)

        json_route = [self.format_location(location) for location in asset.route]

        return {
            'token': asset.token,
            'type': asset.type,
            'profession': asset.profession,
            'active': asset.is_active,
            'carried': asset.carried,
            'size': asset.min_size,
            'abilities': asset.abilities,
            'resources': asset.resources,
            'speed': asset.speed,
            'physical_capacity': asset.physical_capacity,
            'virtual_capacity': asset.virtual_capacity,
            'last_action': asset.last_action,
            'last_action_result': asset.last_action_result,
            'location': self.format_location(asset.location),
            'route': json_route,
            'destination_distance': asset.destination_distance,
            'physical_storage': asset.physical_storage,
            'physical_storage_vector': json_physical_items,
            'virtual_storage': asset.virtual_storage,
            'virtual_storage_vector': json_virtual_items
        }

    @staticmethod
    def format_location(location):
        """Format the attribute location to a dict with the coordinates (Agent protocol)

        :param location: List with the lat and lon coordinate
        :return: Dictionary with the coordinates
        """
        return {'lat': location[0], 'lon': location[1]}

    def jsonify_events(self, events_list):
        """Transform the event into a JSON object.

        It will transform all the victims and the victims inside the photos, the water samples, everything related to
        the event.

        :param events_list: Dictionary with flood, victims, photos and water sampples.
        :return dict: Dictionary with all the elements converted to JSON."""

        formatted_list = []

        for event in events_list:
            if not event:
                pass

            if event.type == 'flood':
                flood = {
                    'identifier': event.id,
                    'type': 'flood',
                    'location': self.format_location(event.dimension['location']),
                    'shape': event.dimension['shape']
                }

                if event.dimension['shape'] == 'circle':
                    flood['radius'] = event.dimension['radius']

                formatted_list.append(flood)

            elif event.type == 'victim':
                victim = {
                    'flood_id': event.flood_id,
                    'identifier': event.identifier,
                    'type': 'victim',
                    'location': self.format_location(event.location),
                    'size': event.size,
                    'lifetime': event.lifetime
                }

                formatted_list.append(victim)

            elif event.type == 'photo':
                photo_victims = []
                for victim in event.victims:
                    if victim.active:
                        json_victim = {
                            'flood_id': victim.flood_id,
                            'identifier': victim.identifier,
                            'type': 'victim',
                            'location': self.format_location(victim.location),
                            'size': victim.size,
                            'lifetime': victim.lifetime
                        }
                        photo_victims.append(json_victim)

                photo = {
                    'flood_id': event.flood_id,
                    'identifier': event.identifier,
                    'type': 'photo',
                    'location': self.format_location(event.location),
                    'size': event.size,
                    'victims': photo_victims
                }

                formatted_list.append(photo)

            else:
                water_sample = {
                    'flood_id': event.flood_id,
                    'identifier': event.identifier,
                    'type': 'water_sample',
                    'location': self.format_location(event.location),
                    'size': event.size
                }

                formatted_list.append(water_sample)

        return formatted_list

    def jsonify_delivered_items(self, items):
        """Transform all the items to JSON.

        The supported items are: victim, photo, water sample, social asset or agent. Any other item is considered
        unknown and only saved the type and identifier of the item.

        :param items: List of the delivered items.
        :return list: List of all the items converted to JSON."""

        json_items = []

        for item in items:
            if item.type == 'victim':
                json_item = {
                    'flood_id': item.flood_id,
                    'identifier': item.identifier,
                    'type': 'victim',
                    'location': self.format_location(item.location),
                    'size': item.size,
                    'lifetime': item.lifetime
                }

            elif item.type == 'photo':
                json_photo_victims = []

                for victim in item.victims:
                    if victim.active:
                        json_victim = {
                            'flood_id': victim.flood_id,
                            'identifier': victim.identifier,
                            'type': 'victim',
                            'location': self.format_location(victim.location),
                            'size': victim.size,
                            'lifetime': victim.lifetime
                        }
                        json_photo_victims.append(json_victim)

                json_item = {
                    'flood_id': item.flood_id,
                    'identifier': item.identifier,
                    'type': 'photo',
                    'location': self.format_location(item.location),
                    'size': item.size,
                    'victims': json_photo_victims
                }

            elif item.type == 'water_sample':
                json_item = {
                    'flood_id': item.flood_id,
                    'identifier': item.identifier,
                    'type': 'water_sample',
                    'location': self.format_location(item.location),
                    'size': item.size
                }

            elif item.type == 'social_asset':
                json_item = self.jsonify_asset(item)

            elif item.type == 'agent':
                json_item = self.jsonify_agent(item)

            else:
                json_item = {
                    'identifier': item.identifier,
                    'type': 'Unknown'
                }

            json_items.append(json_item)

        return json_items

    def jsonify_social_assets(self, social_assets):
        """ Transform the list of social assets into a more readable structure

        :param social_assets: List of the social assets to formatted
        :return: List of dictionaries with the profession and location
        """
        formatted_list = []

        for social_asset in social_assets:
            formatted_list.append({
                'id': social_asset.identifier,
                'profession': social_asset.profession,
                'location': self.format_location(social_asset.location),
                'abilities': social_asset.abilities,
                'resources': social_asset.resources
            })

        return formatted_list

    @staticmethod
    def jsonify_action_token_by_step(action_token_by_step):
        """Transform the list of actions by step into a more readable structure.

        :param action_token_by_step: List of all the actions step by step.
        :return list: List of dictionaries with token and action sent step by step."""

        json_action_token_by_step = []
        for step, action_token_list in action_token_by_step:
            json_token_action = []
            for token, action in action_token_list:
                json_token_action.append({'token': token, 'action': action})

            json_action_token_by_step.append({'step': step, 'token_action': json_token_action})

        return json_action_token_by_step

    @staticmethod
    def jsonify_amount_of_actions_by_step(amount_of_actions_by_step):
        """Transform the list of amount of actions by step to a more readable structure.

        :param amount_of_actions_by_step: List of amount of actions sent step by step.
        :return list: List of dictionaries with the step and amount of actions."""

        return [{'step': step, 'actions_amount': actions_amount} for step, actions_amount in amount_of_actions_by_step]

    @staticmethod
    def jsonify_actions_by_step(actions_by_step):
        """Transform the list of actions by step to a more readable structure.

        :param actions_by_step: List of steps each one with a list of actions sent.
        :return list: List of dictionaries with the step and the list of actions."""

        return [{'step': step, 'actions': actions} for step, actions in actions_by_step]
