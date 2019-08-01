import os
import re
import json
import pathlib
from simulation_engine.copycat import CopyCat


class JsonFormatter:
    """Class that converts all the objects into JSON style dicts."""

    def __init__(self, config):
        config_location = pathlib.Path(__file__).parents[3] / config
        self.copycat = CopyCat(json.load(open(config_location, 'r')))

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

        try:
            response = self.copycat.restart()
            json_agents = self.jsonify_agents(response[0])
            json_assets = self.jsonify_assets(response[1])

            json_actors = [*json_agents, *json_assets]
            json_events = self.jsonify_events(response[2])

            return {'status': 1, 'actors': json_actors, 'event': json_events, 'message': 'Simulation restarted.'}

        except Exception as e:
            return {'status': 0, 'actors': [], 'event': {}, 'message': f'An error occurred during restart: "{str(e)}"'}

    def connect_agent(self, token):
        """Connect the agent to the simulation and returns a JSON response.

        :param token: The generated token for the agent.
        :return dict: Dictionary with status representing if any errors were found and a general message."""

        try:
            response = self.copycat.connect_agent(token)
            if response:
                return {'status': 1, 'message': 'Agent connected.'}

            else:
                return {'status': 0, 'message': 'Agent could not connect.'}

        except Exception as e:
            return {'status': 0, 'message': f'An error occurred during connection: {str(e)}.'}

    def connect_social_asset(self, token):
        """Connect the social asset to the simulation and returns a JSON response.

        :param token: The generated token for the social asset.
        :return dict: Dictionary with status representing if any errors were found, the social asset object and a
        general message."""

        try:
            response = self.copycat.connect_social_asset(token)
            if response is not None:
                return {'status': 1, 'social_asset': self.jsonify_asset(response), 'message': 'Social asset connected.'}

            else:
                return {'status': 0, 'social_asset': {}, 'message': 'Social asset could not connect.'}

        except Exception as e:
            return {'status': 0, 'social_asset': {}, 'message': f'An error occurred during connection: {str(e)}.'}

    def disconnect_agent(self, token):
        """Disconnect the agent to the simulation and returns a JSON response.

        :param token: The generated token for the agent.
        :return dict: Dictionary with status representing if any errors were found and a general message."""

        try:
            response = self.copycat.disconnect_agent(token)

            if response:
                return {'status': 1, 'message': 'Agent disconnected.'}

            else:
                return {'status': 0, 'message': 'Agent is not connected.'}

        except Exception as e:
            return {'status': 0, 'message': f'An error occurred during disconnection: {str(e)}.'}

    def disconnect_social_asset(self, token):
        """Disconnect the social asset to the simulation and returns a JSON response.

        :param token: The generated token for the social asset.
        :return dict: Dictionary with status representing if any errors were found and a general message."""

        try:
            response = self.copycat.disconnect_social_asset(token)

            if response:
                return {'status': 1, 'message': 'Social asset disconnected.'}

            else:
                return {'status': 0, 'message': 'Social asset is not connected.'}

        except Exception as e:
            return {'status': 0, 'message': f'An error occurred during disconnection: {str(e)}.'}

    def start(self):
        """Start the simulation and returns a JSON response.

        All the agents, social assets and events are converted, the copycat class prevents from the formatter changing
        the objects inside the engine.

        :return dict: Dictionary with status representing if any errors were found, the list of agents and social assets,
        the event with the flood, victims, photos and water samples and a general message."""

        try:
            response = self.copycat.start()
            json_agents = self.jsonify_agents(response[0])
            json_assets = self.jsonify_assets(response[1])

            json_actors = [*json_agents, *json_assets]
            json_events = self.jsonify_events(response[2])

            return {'status': 1, 'actors': json_actors, 'event': json_events, 'message': 'Simulation started.'}

        except Exception as e:
            return {'status': 0, 'actors': [], 'event': {}, 'message': f'An error occurred during restart: "{str(e)}"'}

    def do_step(self, token_action_list):
        """Do a step on the simulation.

        After the step, all the results from the actions are converted to JSON.

        :param token_action_list: List with all the tokens combined with the action|parameter sent.
        :return dict: Dictionary with a status representing if any errors were found, the list of agents and social
        assets, the event with the flood, victims, photos, and water samples and a general message."""

        try:
            response = self.copycat.do_step(token_action_list)
            if response is None:
                return {'status': 1, 'actors': [], 'event': {}, 'message': 'Simulation finished.'}

            json_actors = []
            for obj in response[0]:
                if 'agent' in obj:
                    json_actors.append({'agent': self.jsonify_agent(obj['agent']), 'message': obj['message']})
                else:
                    json_actors.append({'social_asset': self.jsonify_asset(obj['social_asset']), 'message': obj['message']})

            json_events = self.jsonify_events(response[1])

            return {'status': 1, 'actors': json_actors, 'event': json_events, 'message': 'Step completed.'}

        except Exception as e:
            return {'status': 0, 'actors': [], 'event': {}, 'message': f'An error occurred during step: "{str(e)}"'}

    def save_logs(self):
        """Write all the saved logs to a file on the root of the project, the file will be inside a folder structure
        based on the date and time the simulation ran."""

        year, month, day, hour, minute, config_file, logs = self.copycat.get_logs()
        path = pathlib.Path(__file__).parents[3] / str(year) / str(month) / str(day) / str(config_file)

        os.makedirs(str(path.absolute()), exist_ok=True)

        hour = '{:0>2d}'.format(hour)
        minute = '{:0>2d}'.format(minute)

        for log in logs:
            json_items = self.jsonify_delivered_items(logs[log]['environment']['delivered_items'])
            json_agents = self.jsonify_agents(logs[log]['agents']['agents'])
            json_active_agents = self.jsonify_agents(logs[log]['agents']['active_agents'])
            json_action_token_by_step = self.jsonify_action_token_by_step(logs[log]['actions']['action_token_by_step'])
            json_acts_by_step = self.jsonify_amount_of_actions_by_step(logs[log]['actions']['amount_of_actions_by_step'])
            json_actions_by_step = self.jsonify_actions_by_step(logs[log]['actions']['actions_by_step'])

            logs[log]['environment']['delivered_items'] = json_items
            logs[log]['agents']['agents'] = json_agents
            logs[log]['agents']['active_agents'] = json_active_agents
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
        """Transform a single agent into a JSON object.

        The keys of the dict were organized from priority and relation to make easier for the user to read it.

        :param agent: The agent object saved in the simulation.
        :return dict: Dictionary with all the information from the agent."""

        json_physical_items = self.jsonify_delivered_items(agent.physical_storage_vector)

        json_virtual_items = self.jsonify_delivered_items(agent.virtual_storage_vector)

        json_route = [list(location) for location in agent.route]

        return {
            'token': agent.token,
            'active': agent.is_active,
            'last_action': agent.last_action,
            'last_action_result': agent.last_action_result,
            'role': agent.role,
            'location': list(agent.location),
            'route': json_route,
            'destination_distance': agent.destination_distance,
            'abilities': agent.abilities,
            'resources': agent.resources,
            'battery': agent.actual_battery,
            'max_charge': agent.max_charge,
            'speed': agent.speed,
            'size': agent.size,
            'social_assets_vector': self.jsonify_assets(agent.social_assets),
            'physical_storage': agent.physical_storage,
            'physical_capacity': agent.physical_capacity,
            'physical_storage_vector': json_physical_items,
            'virtual_storage': agent.virtual_storage,
            'virtual_capacity': agent.virtual_capacity,
            'virtual_storage_vector': json_virtual_items
        }

    def jsonify_asset(self, asset):
        """Transform a single social asset into a JSON object.

        The keys of the dict were organized from priority and relation to make easier for the user to read it.

        :param asset: The social asset object saved in the simulation.
        :return dict: Dictionary with all the information from the social asset."""

        json_physical_items = self.jsonify_delivered_items(asset.physical_storage_vector)

        json_virtual_items = self.jsonify_delivered_items(asset.virtual_storage_vector)

        json_route = [list(location) for location in asset.route]

        return {
            'token': asset.token,
            'active': asset.is_active,
            'last_action': asset.last_action,
            'last_action_result': asset.last_action_result,
            'profession': asset.profession,
            'location': list(asset.location),
            'route': json_route,
            'destination_distance': asset.destination_distance,
            'abilities': asset.abilities,
            'resources': asset.resources,
            'speed': asset.speed,
            'size': asset.size,
            'social_assets_vector': self.jsonify_assets(asset.social_assets),
            'physical_storage': asset.physical_storage,
            'physical_capacity': asset.physical_capacity,
            'physical_storage_vector': json_physical_items,
            'virtual_storage': asset.virtual_storage,
            'virtual_capacity': asset.virtual_capacity,
            'virtual_storage_vector': json_virtual_items
        }

    @staticmethod
    def jsonify_events(events_list):
        """Transform the event into a JSON object.

        It will transform all the victims and the victims inside the photos, the water samples, everything related to
        the event.

        :param events_list: Dictionary with flood, victims, photos and water sampples.
        :return dict: Dictionary with all the elements converted to JSON."""

        if events_list['flood'] is None:
            return {'flood': '', 'victims': [], 'water_samples': [], 'photos': []}

        json_flood = {
            'identifier': events_list['flood'].identifier,
            'type': 'flood',
            'location': list(events_list['flood'].dimensions['location']),
            'shape': events_list['flood'].dimensions['shape']
        }

        if events_list['flood'].dimensions['shape'] == 'circle':
            json_flood['radius'] = events_list['flood'].dimensions['radius']

        json_victims = []
        for victim in events_list['victims']:
            json_victim = {
                'identifier': victim.identifier,
                'type': 'victim',
                'location': list(victim.location),
                'size': victim.size,
                'lifetime': victim.lifetime
            }
            json_victims.append(json_victim)

        json_water_samples = []
        for water_sample in events_list['water_samples']:
            json_water_sample = {
                'identifier': water_sample.identifier,
                'type': 'water_sample',
                'location': list(water_sample.location),
                'size': water_sample.size
            }
            json_water_samples.append(json_water_sample)

        json_photos = []
        for photo in events_list['photos']:
            json_photo_victims = []
            for victim in photo.victims:
                if victim.active:
                    json_victim = {
                        'identifier': victim.identifier,
                        'type': 'victim',
                        'location': list(victim.location),
                        'size': victim.size,
                        'lifetime': victim.lifetime
                    }
                    json_photo_victims.append(json_victim)

            json_photo = {
                'identifier': photo.identifier,
                'type': 'photo',
                'location': list(photo.location),
                'size': photo.size,
                'analyzed': photo.analyzed,
                'victims': json_photo_victims
            }

            json_photos.append(json_photo)

        return {'flood': json_flood, 'victims': json_victims, 'water_samples': json_water_samples, 'photos': json_photos}

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
                    'identifier': item.identifier,
                    'type': 'victim',
                    'location': list(item.location),
                    'size': item.size,
                    'lifetime': item.lifetime
                }

            elif item.type == 'photo':
                json_photo_victims = []

                for victim in item.victims:
                    json_victim = {
                        'identifier': victim.identifier,
                        'type': 'victim',
                        'location': list(victim.location),
                        'size': victim.size,
                        'lifetime': victim.lifetime
                    }
                    json_photo_victims.append(json_victim)

                json_item = {
                    'identifier': item.identifier,
                    'type': 'photo',
                    'location': list(item.location),
                    'size': item.size,
                    'victims': json_photo_victims
                }

            elif item.type == 'water_sample':
                json_item = {
                    'identifier': item.identifier,
                    'type': 'water_sample',
                    'location': list(item.location),
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

    @staticmethod
    def jsonify_action_token_by_step(action_token_by_step):
        """Transform the list of actions by step into a more readable structure.

        :param action_token_by_step: List of all the actions step by step.
        :return list: List of dictionaries with token and action sent step by step."""

        json_action_token_by_step = []
        for step, action_token_list in action_token_by_step:
            json_token_action = []
            for action, token in action_token_list:
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
