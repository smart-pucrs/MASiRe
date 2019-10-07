"""This module formats the different events to send to the agents and social assets.

Note: The response does not have agent or social asset as key until they are processed."""


def initial_percepts_format(response, token):
    info = {'type': 'initial_percepts', 'map_percepts': {}, 'agent_percepts': {}}

    if response:
        if response['status']:

            found_index = 0
            for idx, agent in enumerate(response['agents']):
                if 'agent' in agent:
                    if agent['agent']['token'] == token:
                        info['agent_percepts'] = agent_constants(agent['agent'])
                        found_index = idx
                        break

                else:
                    if agent['asset']['token'] == token:
                        info['agent_percepts'] = asset_constants(agent['asset'])
                        found_index = idx
                        break

            if not info['agent_percepts']:
                return event_error_format('Actor not found in response.')

            info['map_percepts'] = format_map_percepts_agents(response['map_percepts'])
            response['agents'].pop(found_index)

            return info
        else:
            return event_error_format(response['message'])
    else:
        return event_error_format('Empty simulation response. ')


def format_map_percepts_agents(map_percepts):
    return {
        'proximity': map_percepts['proximity'],
        'minLat': map_percepts['minLat'],
        'maxLat': map_percepts['maxLat'],
        'minLon': map_percepts['minLon'],
        'maxLon': map_percepts['maxLon'],
        'centerLat': map_percepts['centerLat'],
        'centerLon': map_percepts['centerLon']
    }


def percepts_format(response, token):
    info = {'type': 'percepts', 'environment': {}, 'message': ''}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            found_index = 0
            for idx, actor in enumerate(response['actors']):
                if 'agent' in actor:
                    if actor['agent']['token'] == token:
                        info['agent'] = agent_variables(actor['agent'])
                        info['message'] = actor['message']
                        found_index = idx
                        break
                else:
                    if actor['asset']['token'] == token:
                        info['agent'] = asset_variables(actor['asset'])
                        info['message'] = actor['message']
                        found_index = idx
                        break

            if 'agent' not in info:
                return event_error_format('Actor not found in response. ')

            response['actors'].pop(found_index)
            info['environment'] = response['environment']

        else:
            event_error_format(response['message'])

        return info

    else:
        return event_error_format('Empty simulation response. ')


def end_format(response, token):
    if response:
        if response['status']:
            if token in response['report'].keys():
                return {'type': 'end', 'report': response['report'][token]}

            return event_error_format('Report not found.')
        else:
            return event_error_format(response['message'])
    else:
        return event_error_format('Empty simulation response.')


def bye_format(response, token):
    if response:
        if response['status']:
            if token in response['report'].keys():
                return {'type': 'bye', 'report': response['report'][token]}

            return event_error_format('Report not found.')
        else:
            return event_error_format(response['message'])
    else:
        return event_error_format('Empty simulation response.')


def event_error_format(message):
    """Build a typical error response for the agents. When this function is called, it is very probably that an internal
    error occurred."""

    return {'type': 'error', 'message': f'{message}Possible internal error.'}


def initial_percepts_monitor_format(response):
    info = {'status': 0, 'map_percepts': None, 'message': ''}

    if response:
        if response['status']:
            if 'map_percepts' in response:
                info['map_percepts'] = response['map_percepts']
                info['status'] = 1
            else:
                info['message'] = 'Error formatting initial_percepts into API.'
        else:
            info['message'] = response['message']
    else:
        info['message'] = 'Empty simulation response.'

    return info


def percepts_monitor_format(response):
    info = {'status': 0, 'actors': None, 'environment': None, 'message': ''}

    if response:
        if response['status']:
            if 'actors' not in response:
                info['message'] = 'Error formatting percepts into API, key "actors" not found in response.'
            elif 'environment' not in response:
                info['message'] = 'Error formatting percepts into API, key "environment" not found in response.'
            else:
                info['status'] = 1

                actors = []
                for actor in response['actors']:
                    if 'agent' in actor:
                        actors.append(monitor_agent_info(actor['agent']))
                    else:
                        actors.append(monitor_asset_info(actor['asset']))

                info['actors'] = actors
                info['environment'] = response['environment']
        else:
            info['message'] = response['message']
    else:
        info['message'] = 'Empty simulation response.'

    return info


def end_monitor_format(response):
    info = {'status': 0, 'report': None, 'message': ''}

    if response:
        if response['status']:
            info['status'] = 1
            info['report'] = response['report']
        else:
            info['message'] = response['message']
    else:
        info['message'] = 'Empty simulation response.'

    return info


def bye_monitor_format(response):
    info = {'status': 0, 'report': None, 'message': ''}

    if response:
        if response['status']:
            info['status'] = 1
            info['report'] = response['report']
        else:
            info['message'] = response['message']
    else:
        info['message'] = 'Empty simulation response.'

    return info


def event_error_monitor_format(message):
    return {'message': f'{message}Possible internal error.'}


def monitor_agent_info(agent):
    return {
        'type': agent['type'],
        'role': agent['role'],
        'location': agent['location'],
    }


def monitor_asset_info(asset):
    return {
        'type': asset['type'],
        'profession': asset['profession'],
        'location': asset['location'],
    }


def agent_constants(agent):
    return {
        'token': agent['token'],
        'role': agent['role'],
        'abilities': agent['abilities'],
        'resources': agent['resources'],
        'max_charge': agent['max_charge'],
        'speed': agent['speed'],
        'size': agent['size'],
        'physical_capacity': agent['physical_capacity'],
        'virtual_capacity': agent['virtual_capacity']
    }


def agent_variables(agent):
    physical_storage_vector = []

    for item in agent['physical_storage_vector']:
        if item['type'] == 'agent':
            json_agent = {
                'token': item['token'],
                'role': item['role']
            }

            physical_storage_vector.append(json_agent)
        elif item['type'] == 'asset':
            json_asset = {
                'token': item['token'],
                'profession': item['profession']
            }

            physical_storage_vector.append(json_asset)

        else:
            physical_storage_vector.append(item)

    return {
        'token': agent['token'],
        'active': agent['active'],
        'last_action': agent['last_action'],
        'last_action_result': agent['last_action_result'],
        'location': agent['location'],
        'route': agent['route'],
        'destination_distance': agent['destination_distance'],
        'battery': agent['battery'],
        'physical_storage': agent['physical_storage'],
        'physical_storage_vector': physical_storage_vector,
        'virtual_storage': agent['virtual_storage'],
        'virtual_storage_vector': agent['virtual_storage_vector'],
        'social_assets': agent['social_assets']
    }


def asset_constants(asset):
    return {
        'token': asset['token'],
        'profession': asset['profession'],
        'abilities': asset['abilities'],
        'resources': asset['resources'],
        'speed': asset['speed'],
        'size': asset['size'],
        'physical_capacity': asset['physical_capacity'],
        'virtual_capacity': asset['virtual_capacity']
    }


def asset_variables(agent):
    return {
        'token': agent['token'],
        'active': agent['active'],
        'last_action': agent['last_action'],
        'last_action_result': agent['last_action_result'],
        'location': agent['location'],
        'route': agent['route'],
        'destination_distance': agent['destination_distance'],
        'physical_storage': agent['physical_storage'],
        'physical_storage_vector': agent['physical_storage_vector'],
        'virtual_storage': agent['virtual_storage'],
        'virtual_storage_vector': agent['virtual_storage_vector'],
    }
