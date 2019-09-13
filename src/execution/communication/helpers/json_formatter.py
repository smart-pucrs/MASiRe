"""This module formats the different events to send to the agents and social assets.

Note: The response does not have agent or social asset as key until they are processed."""


def initial_percepts_format(response, token):
    info = {'type': 'initial_percepts', 'map_percepts': {}, 'agent_percepts': {}}

    for agent in response['agents']:
        if agent['token'] == token:
            info['agent_percepts'] = agent
            info['map_percepts'] = response['map_percepts']

            return info

    return event_error_format('Agent not found.')


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
    if token in response.keys():
        return {'type': 'end', 'report': response[token]}

    return event_error_format('A error occurred in API.')


def bye_format(response, token):
    if token in response['report'].keys():
        return {'type': 'bye', 'report': response['report'][token]}

    return event_error_format(response['message'])


def event_error_format(message):
    """Build a typical error response for the agents. When this function is called, it is very probably that an internal
    error occurred."""

    return {'type': 'error', 'message': f'{message}Possible internal error.'}

