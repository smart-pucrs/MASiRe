import copy
import json
import sys
import pathlib
import pytest

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

@pytest.fixture
def game_state():
    from src.execution.simulation_engine.simulation_helpers.cycle import Cycle
    config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
    config_json = json.load(open(config_path, 'r'))
    return Cycle(config_json, False, False)

def test_connection(game_state):
    assert game_state.connect_agent('token_temp')
    assert game_state.disconnect_agent('token_temp')

def test_asset_connection(game_state):
    token = 'agent_temp'
    game_state.connect_agent(token)
    agents, req = game_state.execute_actions([{'token': token, 'action': 'searchSocialAsset', 'parameters': [1000]}])
    assert req == []
    agents, req = game_state.execute_actions([{'token': token, 'action': 'requestSocialAsset', 'parameters': [0]}])
    assert req[0] == token
    game_state.connect_social_asset('agent_temp', 'token_disconnect')
    assert game_state.disconnect_social_asset('token_disconnect')

def test_activate_step(game_state):
    old = game_state.get_step()
    assert old == []

    game_state.activate_step()
    new = game_state.get_step()
    assert new[0].active

def test_get_previous_steps(game_state):
    for i in range(1, 5):
        game_state.current_step = i
        game_state.activate_step()

    assert game_state.get_previous_steps()


def test_check_steps(game_state):
    assert not game_state.check_steps()
    game_state.current_step = 10
    assert game_state.check_steps()
    game_state.current_step = 4


def test_update_steps(game_state):
    # TODO: retest this
    return
    old_period = game_state.steps[0]['flood'].period
    game_state.update_steps()
    new_period = game_state.steps[0]['flood'].period

    assert old_period != new_period

def test_missing_actions(game_state):
    game_state.connect_agent('token_temp1')
    game_state.connect_agent('token_temp2')    
    agent1 = game_state.agents_manager.get('token_temp1')
    agent2 = game_state.agents_manager.get('token_temp2')
    actions = [{'token': agent1.token, 'action': 'deliverAgent', 'parameters': [agent2.token]}, {'token': agent2.token, 'action': 'blabla', 'parameters': [agent1.token]}]
    game_state.execute_actions(actions)
    assert agent1.last_action == 'deliverAgent'
    assert agent1.last_action_result != 'success'
    assert agent2.last_action == 'blabla'
    assert agent2.last_action_result != 'success'
    game_state.disconnect_agent('token_temp1')
    game_state.disconnect_agent('token_temp2')

def test_restart(game_state):
    game_state.connect_agent('token1_agent')
    game_state.connect_agent('token2_agent')    
    game_state.agents_manager.edit('token1_agent', 'carried', True)
    game_state.agents_manager.edit('token1_agent', 'is_active', False)
    game_state.social_assets_manager.edit('token1_asset', 'carried', True)
    game_state.social_assets_manager.edit('token1_asset', 'is_active', False)
    game_state.restart(config_json, False, False)
    assert not game_state.steps[0]['flood'].active
    assert game_state.current_step == 0
    assert not game_state.delivered_items
    assert not game_state.agents_manager.get('token2_agent').carried
    assert game_state.agents_manager.get('token2_agent').is_active
    assert len(game_state.social_assets_manager.get_tokens()) == 0
    game_state.disconnect_agent('token1_agent')
    game_state.disconnect_agent('token2_agent')