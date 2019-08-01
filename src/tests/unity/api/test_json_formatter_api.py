import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

from src.execution.communication.helpers.json_formatter import *


def test_event_error_format():
    resp = event_error_format('Test error. ')
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert resp['message'].startswith('Test error. ')
    assert not resp['event']


def test_simulation_started_format_agent_no_error():
    response_ok = {
        'status': 1,
        'actors': [{'token': 'agent1', 'role': 'rolename'}],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Ok.'
    }
    response_status_0 = {
        'status': 0,
        'actors': [{'token': 'agent1', 'role': 'rolename'}],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Agent error.'
    }

    resp = simulation_started_format(response_ok, 'agent1')
    assert resp
    assert resp['result']
    assert resp['agent']
    assert resp['message'] == 'Ok.'

    resp = simulation_started_format(response_status_0, 'agent1')
    assert resp
    assert not resp['result']
    assert resp['message'] == 'Agent error.'


def test_simulation_started_format_asset_no_error():
    response_ok = {
        'status': 1,
        'actors': [{'token': 'asset1', 'profession': 'professionname'}],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Ok.'
    }
    response_status_0 = {
        'status': 0,
        'actors': [{'token': 'asset1', 'profession': 'professionname'}],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Social asset error.'
    }

    resp = simulation_started_format(response_ok, 'asset1')
    assert resp
    assert resp['result']
    assert resp['social_asset']
    assert resp['message'] == 'Ok.'

    resp = simulation_started_format(response_status_0, 'asset1')
    assert resp
    assert not resp['result']
    assert resp['message'] == 'Social asset error.'


def test_simulation_started_format_error():
    response_no_token_match = {
        'status': 1,
        'actors': [{'token': 'agent1', 'role': 'rolename'}],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Ok.'
    }
    response_empty = {}

    resp = simulation_started_format(response_no_token_match, 'asset1')
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert resp['message'].startswith('Actor not found in response. ')

    resp = simulation_started_format(response_empty, 'agent1')
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert resp['message'].startswith('Empty simulation response. ')


def test_simulation_ended_format():
    response_ok = {
        'status': 1,
        'message': 'Ok.'
    }

    response_status_0 = {
        'status': 0,
        'message': 'Error.'
    }

    response_empty = {}

    resp = simulation_ended_format(response_ok)
    assert resp
    assert resp['status'] == 1
    assert resp['result']
    assert resp['message'] == 'Ok.'

    resp = simulation_ended_format(response_status_0)
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert resp['message'] == 'Error.'

    resp = simulation_ended_format(response_empty)
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert resp['message'].startswith('Empty response. ')


def test_action_results_format_agent_no_error():
    response_ok = {
        'status': 1,
        'actors': [
            {'agent': {'token': 'agent1', 'role': 'rolename'}, 'message': 'Ok agent1'},
            {'agent': {'token': 'agent2', 'role': 'rolename'}, 'message': 'Ok agent2'},
            {'agent': {'token': 'agent3', 'role': 'rolename'}, 'message': 'Ok agent3'}
        ],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Ok.'
    }

    response_status_0 = {
        'status': 0,
        'actors': [
            {'agent': {'token': 'agent1', 'role': 'rolename'}, 'message': 'Ok agent1'},
            {'agent': {'token': 'agent2', 'role': 'rolename'}, 'message': 'Ok agent2'},
            {'agent': {'token': 'agent3', 'role': 'rolename'}, 'message': 'Ok agent3'}
        ],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Error.'
    }

    resp = action_results_format(response_ok, 'agent1')
    assert resp
    assert resp['result']
    assert resp['agent']
    assert resp['message'] == 'Ok agent1'

    resp = action_results_format(response_ok, 'agent3')
    assert resp
    assert resp['result']
    assert resp['agent']
    assert resp['message'] == 'Ok agent3'

    resp = action_results_format(response_status_0, 'agent1')
    assert resp
    assert resp['result'] == 0
    assert not resp['result']
    assert not resp['event']
    assert 'agent' not in resp
    assert 'social_asset' not in resp
    assert resp['message'] == 'Error.'


def test_action_results_format_asset_no_error():
    response_ok = {
        'status': 1,
        'actors': [
            {'social_asset': {'token': 'asset1', 'profession': 'professionname'}, 'message': 'Ok asset1'},
            {'social_asset': {'token': 'asset2', 'profession': 'professionname'}, 'message': 'Ok asset2'}
        ],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Ok.'
    }

    response_status_0 = {
        'status': 0,
        'actors': [
            {'social_asset': {'token': 'asset1', 'profession': 'professionname'}, 'message': 'Ok asset1'},
            {'social_asset': {'token': 'asset2', 'profession': 'professionname'}, 'message': 'Ok asset2'}
        ],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Error.'
    }

    resp = action_results_format(response_ok, 'asset1')
    assert resp
    assert resp['result']
    assert resp['social_asset']
    assert resp['message'] == 'Ok asset1'

    resp = action_results_format(response_ok, 'asset2')
    assert resp
    assert resp['result']
    assert resp['social_asset']
    assert resp['message'] == 'Ok asset2'

    resp = action_results_format(response_status_0, 'a1')
    assert resp
    assert resp['result'] == 0
    assert not resp['result']
    assert not resp['event']
    assert 'agent' not in resp
    assert 'social_asset' not in resp
    assert resp['message'] == 'Error.'


def test_action_results_format_error():
    response_empty = {}

    response = {
        'status': 1,
        'actors': [
            {'agent': {'token': 'agent1', 'role': 'rolename'}, 'message': 'Ok agent1'},
            {'social_asset': {'token': 'asset1', 'profession': 'professionname'}, 'message': 'Ok asset1'},
            {'agent': {'token': 'agent2', 'role': 'rolename'}, 'message': 'Ok agent2'},
            {'agent': {'token': 'agent3', 'role': 'rolename'}, 'message': 'Ok agent3'},
            {'social_asset': {'token': 'asset2', 'profession': 'professionname'}, 'message': 'Ok asset2'}
        ],
        'event': {'flood': None, 'victims': None, 'photos': None, 'water_samples': None},
        'message': 'Error.'
    }

    resp = action_results_format(response_empty, 'agent1')
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert not resp['event']
    assert resp['message'].startswith('Empty simulation response. ')

    resp = action_results_format(response, 'agent4')
    assert resp
    assert resp['status'] == 0
    assert not resp['result']
    assert not resp['event']
    assert resp['message'].startswith('Actor not found in response. ')


if __name__ == '__main__':
    test_event_error_format()
    test_simulation_started_format_agent_no_error()
    test_simulation_started_format_asset_no_error()
    test_simulation_started_format_error()
    test_simulation_ended_format()
    test_action_results_format_agent_no_error()
    test_action_results_format_asset_no_error()
    test_action_results_format_error()
