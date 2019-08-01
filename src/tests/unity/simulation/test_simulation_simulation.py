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
simulation = Simulation(config_json)


def test_connect_agent():
    assert simulation.connect_agent('token1_agent')


def test_connect_social_asset():
    assert simulation.connect_social_asset('token1_asset')


def test_disconnect_agent():
    assert simulation.disconnect_agent('token1_agent')


def test_disconnect_social_asset():
    assert simulation.disconnect_social_asset('token1_asset')


def test_start():
    agents, assets, step = simulation.start()
    assert not agents
    assert not assets
    assert step
    assert step['flood'].active


def test_do_step():
    actions_tokens_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': ['token2_agent']},
        {'token': 'token3_agent', 'action': 'pass', 'parameters': []},
        {'token': 'token3_asset', 'action': 'rescueVictim', 'parameters': []}
    ]

    simulation.connect_agent('token2_agent')
    simulation.connect_social_asset('token2_asset')
    simulation.connect_agent('token3_agent')
    simulation.connect_social_asset('token3_asset')

    action_results, step = simulation.do_step(actions_tokens_list)
    assert action_results
    assert step

    simulation.terminated = True
    resp = simulation.do_step(actions_tokens_list)
    assert resp is None

    simulation.terminated = False


def test_log():
    log = simulation.log()
    assert simulation.cycler.current_step == 2
    assert len(simulation.cycler.steps[0]['water_samples']) == log['environment']['water_samples_ignored']
    assert len(simulation.cycler.steps[0]['photos']) == log['environment']['photos_ignored']
    assert len(simulation.cycler.steps[0]['water_samples']) == log['environment']['water_samples_ignored']
    assert log['environment']['floods_amount'] == 1
    assert log['agents']['active_agents_amount'] == 2
    assert log['agents']['agents_amount'] == 3
    assert log['assets']['active_assets_amount'] == 2
    assert log['assets']['assets_amount'] == 3
    assert log['actions']['amount_of_actions_executed'] == 8
    assert log['actions']['amount_of_actions_by_step'] == [(1, 4), (2, 4)]


def test_restart():
    agents, assets, step = simulation.restart(config_json)
    assert len(agents) == 3
    assert len(assets) == 3
    assert step
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
