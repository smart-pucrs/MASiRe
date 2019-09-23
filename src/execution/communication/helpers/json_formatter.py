"""This module formats the different events to send to the agents and social assets.

Note: The response does not have agent or social asset as key until they are processed."""


def initial_percepts_format(response, token):
    info = {'type': 'initial_percepts', 'map_percepts': {}, 'agent_percepts': {}}

    if response:
        if response['status']:
            for agent in response['agents']:
                if agent['token'] == token:
                    info['agent_percepts'] = agent
                    info['map_percepts'] = response['map_percepts']

                    return info

            return event_error_format('Agent not found.')
        else:
            return event_error_format(response['message'])
    else:
        return event_error_format('Empty simulation response. ')


def percepts_format(response, token):
    info = {'type': 'percepts', 'environment': {}, 'message': ''}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            found_index = 0
            for idx, actor in enumerate(response['actors']):
                if actor['agent']['token'] == token:
                    info['agent'] = actor['agent']
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
                info['actors'] = response['actors']
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
