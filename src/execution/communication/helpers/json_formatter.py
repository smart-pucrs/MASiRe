"""This module formats the different events to send to the agents and social assets.

Note: The response does not have agent or social asset as key until they are processed."""


def simulation_started_format(response, token):
    """Build the response for the token given in the parameters.

    It will loop through all the actors named on the response until if finds the one that matches the token.

    :param response: Response from the engine.
    :param token: Current token."""

    info = {'status': 0, 'result': False, 'environment': {}, 'message': '', 'type': 'percepts'}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            info['environment']['events'] = format_events(response['event'])
            info['environment']['step'] = response['step']

            found_index = 0
            for idx, actor in enumerate(response['actors']):
                if actor['token'] == token:
                    if 'role' in actor:
                        info['agent'] = format_agent(actor)
                    else:
                        info['social_asset'] = actor
                    found_index = idx
                    break

            if 'agent' not in info and 'social_asset' not in info:
                return event_error_format('Actor not found in response. ')

            response['actors'].pop(found_index)
            info['event'] = response['event']

        info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty simulation response. ')


def simulation_ended_format(response):
    """Build the response for the token given in the parameters.

    :param response: Response from the engine."""

    info = {'status': 0, 'result': False, 'event': {}, 'message': ''}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

        info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty response. ')


def action_results_format(response, token):
    """Build the response for the token given in the parameters.

    It will loop through all the actors named on the response until if finds the one that matches the token.

    :param response: Response from the engine.
    :param token: Current token."""

    info = {'status': 0, 'result': False, 'environment': {}, 'message': '', 'type': 'percepts'}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            ########## TEMPORARY CODE ###########
            info['environment']['events'] = format_events(response['event'])
            info['environment']['step'] = response['step']

            found_index = 0
            for idx, actor in enumerate(response['actors']):
                if 'agent' in actor:
                    if actor['agent']['token'] == token:
                        info['agent'] = format_agent(actor['agent'])
                        info['message'] = actor['message']
                        print("Result: ", info['agent'])
                        found_index = idx
                        break
                else:
                    if actor['social_asset']['token'] == token:
                        info['social_asset'] = actor['social_asset']
                        info['message'] = actor['message']
                        found_index = idx
                        break

            if 'agent' not in info and 'social_asset' not in info:
                return event_error_format('Actor not found in response. ')

            response['actors'].pop(found_index)
            info['event'] = response['event']

        else:
            info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty simulation response. ')


########## TEMPORARY CODE ###########
def format_location(location):
    return {'lat': location[0], 'lon': location[1]}


########## TEMPORARY CODE ###########
def format_agent(agent_copy):
    del agent_copy['token']
    del agent_copy['role']
    del agent_copy['abilities']
    del agent_copy['resources']
    del agent_copy['max_charge']
    del agent_copy['speed']
    del agent_copy['size']
    del agent_copy['physical_capacity']
    del agent_copy['virtual_capacity']
    agent_copy['location'] = format_location(agent_copy['location'])

    return agent_copy


########## TEMPORARY CODE ###########
def format_events(old_event):
    events = []

    if old_event['flood']:
        events.append(old_event['flood'])
    events.extend(old_event['victims'])
    events.extend(old_event['photos'])
    events.extend(old_event['water_samples'])

    for event in events:
        event['location'] = format_location(event['location'])
        if event['type'] == 'photo':
            del event['victims']
            del event['analyzed']
    return events


def event_error_format(message):
    """Build a typical error response for the agents. When this function is called, it is very probably that an internal
    error occurred."""

    return {'status': 0, 'result': False, 'event': {}, 'message': f'{message}Possible internal error.'}
