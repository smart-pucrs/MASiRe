import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation import Simulation


config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
simulation = Simulation(config_json, False, False)


def test_connect_agent():
    assert simulation.connect_agent('token1_agent')


def test_connect_social_asset():
    simulation.cycler.social_assets_manager.requests['token1_agent'] = 0
    assert simulation.connect_social_asset('token1_agent', 'token1_asset')


def test_disconnect_agent():
    assert simulation.disconnect_agent('token1_agent')


def test_disconnect_social_asset():
    assert simulation.disconnect_social_asset('token1_asset')


def test_start():
    agents, step_info, current_step, map_percepts = simulation.start()
    assert not agents
    assert step_info[0].type == 'flood'
    assert step_info[0].active
    assert current_step == 1
    assert map_percepts


def test_do_step():
    actions_tokens_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': ['token2_agent']},
        {'token': 'token3_agent', 'action': 'pass', 'parameters': []},
        {'token': 'token3_asset', 'action': 'rescueVictim', 'parameters': []}
    ]

    simulation.cycler.social_assets_manager.requests['token2_agent'] = 0
    simulation.cycler.social_assets_manager.requests['token3_agent'] = 1
    simulation.connect_agent('token2_agent')
    simulation.connect_social_asset('token2_agent', 'token2_asset')
    simulation.connect_agent('token3_agent')
    simulation.connect_social_asset('token3_agent', 'token3_asset')

    action_results, step_info, current_step, requests = simulation.do_step(actions_tokens_list)
    assert action_results
    assert step_info
    assert current_step == 2
    assert not requests

    simulation.terminated = True
    resp = simulation.do_step(actions_tokens_list)
    assert resp is None

    simulation.terminated = False


def test_log():
    log = simulation.log()
    assert simulation.cycler.current_step == 2
    assert len(simulation.cycler.steps[0]['water_samples']) == log['environment']['mud_samples_ignored']
    assert len(simulation.cycler.steps[0]['photos']) == log['environment']['photos_ignored']
    assert log['environment']['floods_amount'] == 1
    assert log['agents']['active_agents_amount'] == 2
    assert log['agents']['agents_amount'] == 3
    assert log['assets']['active_assets_amount'] == 2
    assert log['assets']['assets_amount'] == 3
    assert log['actions']['amount_of_actions_executed'] == 8
    assert log['actions']['amount_of_actions_by_step'] == [(1, 4), (2, 4)]


def test_restart():
    agents, step_info, current_step, map_percepts, report, assets_tokens = simulation.restart(config_json, False, False)
    assert len(agents) == 3
    assert len(assets_tokens) == 2
    assert step_info
    assert current_step == 1
    assert report
    assert not simulation.actions_amount
    assert not simulation.actions_amount_by_step
    assert not simulation.actions_by_step
    assert not simulation.action_token_by_step


if __name__ == '__main__':
    test_connect_agent()
    test_connect_social_asset()
    test_disconnect_agent()
    test_disconnect_social_asset()
    test_start()
    test_do_step()
    test_log()
    test_restart()
