import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

from src.execution.communication.helpers.json_formatter import *


def test_initial_percepts_format():
    agent_percepts = {
        'token': 'agent',
        'role': None,
        'abilities': None,
        'resources': None,
        'max_charge': None,
        'speed': None,
        'size': None,
        'physical_capacity': None,
        'virtual_capacity': None
    }

    asset_percepts = {
        'token': 'asset',
        'profession': None,
        'abilities': None,
        'resources': None,
        'speed': None,
        'size': None,
        'physical_capacity': None,
        'virtual_capacity': None
    }

    map_percepts = {
        'proximity': None,
        'minLat': None,
        'maxLat': None,
        'minLon': None,
        'maxLon': None,
        'centerLat': None,
        'centerLon': None
    }

    responses = {'agents': [{'agent': agent_percepts}, {'asset': asset_percepts}], 'map_percepts': map_percepts, 'status': 1}

    assert initial_percepts_format(None, None)['type'] == 'error'
    assert initial_percepts_format(None, None)['message'] == 'Empty simulation response. Possible internal error.'
    assert initial_percepts_format({'status': 0, 'message': 'fake error. '}, None)['message'] == 'fake error. Possible internal error.'
    assert initial_percepts_format({'agents': [{'agent': {'token': 'fake_token'}}], 'status': 1, 'message': 'OK'}, 'wrong_token')['type'] == 'error'
    assert initial_percepts_format({'agents': [{'agent': {'token': 'fake_token'}}], 'status': 1, 'message': 'OK'}, 'wrong_token')['message'] == 'Actor not found in response. Possible internal error.'
    response = initial_percepts_format(responses, 'agent')

    assert 'type' in response
    assert 'map_percepts' in response
    assert 'agent_percepts' in response
    assert response['type'] == 'initial_percepts'
    assert response['map_percepts'] == map_percepts
    assert response['agent_percepts'] == agent_percepts
    assert len(responses['agents']) == 1

    response = initial_percepts_format(responses, 'asset')

    assert 'type' in response
    assert 'map_percepts' in response
    assert 'agent_percepts' in response
    assert response['type'] == 'initial_percepts'
    assert response['map_percepts'] == map_percepts
    assert response['agent_percepts'] == asset_percepts
    assert len(responses['agents']) == 0


def test_format_map_percepts_agents():
    map_percepts = {
        'proximity': None,
        'minLat': None,
        'maxLat': None,
        'minLon': None,
        'maxLon': None,
        'centerLat': None,
        'centerLon': None,
        'fake_attr1': None,
        'take_attr2': None
    }

    response = format_map_percepts_agents(map_percepts)

    assert 'fake_attr1' not in response
    assert 'fake_attr2' not in response

    assert 'proximity' in response
    assert 'minLat' in response
    assert 'maxLat' in response
    assert 'minLon' in response
    assert 'maxLon' in response
    assert 'centerLat' in response
    assert 'centerLon' in response


def test_percepts_format():
    agent_percepts = {
        'token': 'agent',
        'active': None,
        'last_action': None,
        'last_action_result': None,
        'location': None,
        'route': None,
        'destination_distance': None,
        'battery': None,
        'physical_storage': None,
        'physical_storage_vector': [],
        'virtual_storage': None,
        'virtual_storage_vector': [],
        'social_assets': []
    }

    asset_percepts = {
        'token': 'asset',
        'active': None,
        'last_action': None,
        'last_action_result': None,
        'location': None,
        'route': None,
        'destination_distance': None,
        'physical_storage': None,
        'physical_storage_vector': [],
        'virtual_storage': None,
        'virtual_storage_vector': [],
    }

    assert percepts_format(None, None)['message'] == 'Empty simulation response. Possible internal error.'
    assert percepts_format({'status': 0, 'message': 'not ok. '}, None)['message'] == 'not ok. Possible internal error.'

    responses = {'actors': [{'agent': agent_percepts, 'message': 'ok'}, {'asset': asset_percepts, 'message': 'ok'}], 'environment': None, 'status': 1}
    response = percepts_format(responses, 'agent')
    print(response)
    assert 'type' in response
    assert 'environment' in response
    assert 'agent' in response
    assert 'message' in response

    assert response['type'] == 'percepts'
    assert response['environment'] is None
    assert response['agent'] == agent_percepts
    assert response['message'] == 'ok'
    assert len(responses['actors']) == 1

    response = percepts_format(responses, 'asset')

    assert 'type' in response
    assert 'environment' in response
    assert 'agent' in response
    assert 'message' in response

    assert response['type'] == 'percepts'
    assert response['environment'] is None
    assert response['agent'] == asset_percepts
    assert response['message'] == 'ok'
    assert len(responses['actors']) == 0


def test_end_format():
    assert end_format(None, None)['message'] == 'Empty simulation response. Possible internal error.'
    assert end_format({'status': 0, 'message': 'not ok. '}, None)['message'] == 'not ok. Possible internal error.'
    assert end_format({'status': 1, 'report': {'token1': None}}, 'fake')['message'] == 'Report not found. Possible internal error.'
    assert end_format({'status': 1, 'report': {'token1': None}}, 'token1')['report'] is None


def test_bye_format():
    assert bye_format(None, None)['message'] == 'Empty simulation response. Possible internal error.'
    assert bye_format({'status': 0, 'message': 'not ok. '}, None)['message'] == 'not ok. Possible internal error.'
    assert bye_format({'status': 1, 'report': {'token1': None}}, 'fake')['message'] == 'Report not found. Possible internal error.'
    assert bye_format({'status': 1, 'report': {'token1': None}}, 'token1')['report'] is None


def test_event_error_format():
    assert event_error_format('message. ') == {'type': 'error', 'message': 'message. Possible internal error.'}


if __name__ == '__main__':
    test_initial_percepts_format()
    test_format_map_percepts_agents()
    test_percepts_format()
    test_end_format()
    test_bye_format()
    test_event_error_format()
