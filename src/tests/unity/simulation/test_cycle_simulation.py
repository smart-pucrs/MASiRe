import sys
import pathlib
import pytest

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.cycle import Cycle
from src.execution.simulation_engine.exceptions.exceptions import FailedNoRoute

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
cycle = Cycle(config_json, False, False)

class Item:
    def __init__(self, size, type, identifier):
        self.size = size
        self.type = type
        self.identifier = identifier

# @pytest.fixture(scope="session")
@pytest.fixture(autouse=True,scope="module")
def connect_agents():
    for i in range(1, 5):
        cycle.connect_agent(f'token{i}_agent')

    cycle.execute_actions([{'token': 'token1_agent', 'action': 'searchSocialAsset', 'parameters': [1000]}])
    cycle.execute_actions([{'token': 'token1_agent', 'action': 'requestSocialAsset', 'parameters': [0]}])
    cycle.connect_social_asset('token1_agent', 'token1_asset')
    # cycle.execute_actions([{'token': 'token2_agent', 'action': 'requestSocialAsset', 'parameters': [1]}])
    cycle.social_assets_manager.requests['token2_agent'] = 1
    cycle.connect_social_asset('token2_agent', 'token2_asset')
    pass

def test_connection():
    assert cycle.connect_agent('token_temp')
    assert cycle.disconnect_agent('token_temp')


def test_disconnect_asset():
    cycle.social_assets_manager.requests['token1_agent'] = 0
    cycle.connect_social_asset('token1_agent', 'token_disconnect')
    assert cycle.disconnect_social_asset('token_disconnect')

def test_activate_step():
    old = cycle.get_step()
    assert old == []

    cycle.activate_step()
    new = cycle.get_step()
    assert new[0].active


def test_get_step():
    # TODO: dont know what this test does
    return
    assert cycle.get_step()


def test_get_previous_steps():
    for i in range(1, 5):
        cycle.current_step = i
        cycle.activate_step()

    assert cycle.get_previous_steps()


def test_check_steps():
    assert not cycle.check_steps()
    cycle.current_step = 10
    assert cycle.check_steps()
    cycle.current_step = 4


def test_update_steps():
    # TODO: retest this
    return
    old_period = cycle.steps[0]['flood'].period
    cycle.update_steps()
    new_period = cycle.steps[0]['flood'].period

    assert old_period != new_period

def test_check_abilities_and_resources():
    assert cycle._check_abilities_and_resources('token1_agent', 'deliverVirtual')
    assert not cycle._check_abilities_and_resources('token1_agent', 'deliverPhysical')
    
    assert cycle._check_abilities_and_resources('token1_agent', 'charge')
    assert not cycle._check_abilities_and_resources('token1_agent', 'rescueVictim')


def test_charge():
    loc = config_json['map']['maps'][0]['centerLat'], config_json['map']['maps'][0]['centerLon']
    cycle.agents_manager.edit('token1_agent', 'location', loc)
    assert cycle._charge_agent('token1_agent', []) is None


def test_charge_failed_param():
    try:
        cycle._charge_agent('token1_agent', ['parameter_given'])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_charge_failed_location():
    cycle.agents_manager.edit('token1_agent', 'location', [120, 120])
    try:
        cycle._charge_agent('token1_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_move_agent():
    agent = cycle.agents_manager.get('token3_agent')
    loc = list(agent.location)
    loc[0] = loc[0] + 5
    loc[1] = loc[1] + 5

    actions = [{'token': 'token3_agent', 'action': 'move', 'parameters': [*loc]}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token3_agent', results)
    assert agent.last_action == 'move'
    assert agent.last_action_result == 'success'
    assert agent.location is not None
    assert agent.route
    assert agent.destination_distance
    old_dist = [agent.destination_distance]

    cycle.execute_actions(actions)
    cycle.execute_actions(actions)

    results = cycle.execute_actions([{'token': 'token3_agent', 'action': 'move', 'parameters': ['unknown_facility']}])
    agent = get_result_agent('token3_agent', results)
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

    results = cycle.execute_actions([{'token': 'token3_agent', 'action': 'move', 'parameters': []}])
    agent = get_result_agent('token3_agent', results)
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

    loc = ['cdm']
    results = cycle.execute_actions([{'token': 'token3_agent', 'action': 'move', 'parameters': [*loc]}])
    agent = get_result_agent('token3_agent', results)
    assert agent.last_action == 'move'
    assert agent.last_action_result == 'success'

    cycle.agents_manager.edit('token3_agent', 'actual_battery', 0)
    results = cycle.execute_actions([{'token': 'token3_agent', 'action': 'move', 'parameters': [*loc]}])
    agent = get_result_agent('token3_agent', results)
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

    # assert cycle.agents_manager.get('token3_agent').route
    # assert cycle.agents_manager.get('token3_agent').destination_distance
    # assert old_dist[0] != cycle.agents_manager.get('token3_agent').destination_distance

def test_move_agent_failed_unable():
    cycle.connect_agent("agent")
    cycle.agents_manager.edit('agent', 'abilities', ['hybridMovement'])
    cycle.agents_manager.edit('agent', 'location', [10, 10])
    cycle.map.movement_restrictions['groundMovement'] = 100
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].nodes[3])

    result = cycle._execute_agent_action('agent', 'move', loc)
    assert result['message'] != ''

def test_move_asset():
    cycle.social_assets_manager.edit('token1_asset', 'active', True)
    asset = cycle.social_assets_manager.get('token1_asset')
    loc = list(asset.location)
    loc[0] = loc[0] + 0.1
    loc[1] = loc[1] + 0.1

    assert cycle._move_asset('token1_asset', loc) is None
    assert cycle.social_assets_manager.get('token1_asset').route
    assert cycle.social_assets_manager.get('token1_asset').destination_distance

    cycle.social_assets_manager.edit('token1_asset', 'location', loc)
    loc = ['cdm']

    assert cycle._move_asset('token1_asset', loc) is None
    assert cycle.social_assets_manager.get('token1_asset').route
    assert cycle.social_assets_manager.get('token1_asset').destination_distance


def test_move_asset_failed_facility():
    try:
        cycle._move_asset('token3_asset', ['unknown_facility'])
        assert False
    except Exception as e:
        if str(e).endswith('Unknown facility.'):
            assert True
        else:
            assert False


def test_move_asset_failed_less_parameters():
    try:
        cycle._move_asset('token3_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_move_asset_failed_more_parameters():
    try:
        cycle._move_asset('token3_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_move_asset_failed_unable():
    cycle.social_assets_manager.edit('token1_asset', 'is_active', True)
    cycle.social_assets_manager.edit('token1_asset', 'abilities', ['groundMovement'])
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    cycle.map.movement_restrictions['groundMovement'] = 100
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].nodes[3])
    try:
        cycle._move_asset('token1_asset', loc)
        assert False
    except Exception as e:
        if str(e.message).endswith('Asset is not capable of entering Event locations.'):
            assert True
        else:
            assert False


def test_rescue_victim_agent():
    cycle.steps[0]['victims'][0].active = True
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', victim_loc)

    old_storage = [cycle.agents_manager.get('token4_agent').physical_storage]
    actions = [{'token': 'token4_agent', 'action': 'rescueVictim', 'parameters': []}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)

    assert agent.physical_storage_vector
    assert agent.physical_storage != old_storage[0]


def test_rescue_victim_agent_failed_param():
    try:
        cycle._rescue_victim_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_rescue_victim_agent_failed_unknown():
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    try:
        cycle._rescue_victim_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('No victim by the given location is known.'):
            assert True
        else:
            assert False


def test_rescue_victim_asset():
    cycle.steps[0]['victims'][0].active = True
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.social_assets_manager.edit('token1_asset', 'location', victim_loc)
    cycle.current_step = 1

    old_storage = [cycle.social_assets_manager.get('token1_asset').physical_storage]
    assert cycle._rescue_victim_asset('token1_asset', []) is None

    asset = cycle.social_assets_manager.get('token1_asset')
    assert asset.physical_storage_vector
    assert asset.physical_storage != old_storage[0]


def test_rescue_victim_asset_failed_param():
    try:
        cycle._rescue_victim_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_rescue_victim_asset_failed_unknown():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    try:
        cycle._rescue_victim_asset('token1_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('No victim by the given location is known.'):
            assert True
        else:
            assert False

def get_result_agent(token, results):
    for r in results[0]:
        if r['agent'].token == token:
            return r['agent']
    return None

def test_collect_water():
    cycle.steps[0]['water_samples'][0].active = True
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)

    actions = [{'token': 'token4_agent', 'action': 'collectWater', 'parameters': [1]}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action == 'collectWater'
    assert agent.last_action_result != 'success'

    actions = [{'token': 'token4_agent', 'action': 'collectWater', 'parameters': []}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action == 'collectWater'
    assert agent.last_action_result == 'success'

def test_collect_water_asset():
    cycle.steps[0]['water_samples'][0].active = True
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get('token1_asset').physical_storage]
    assert cycle._collect_water_asset('token1_asset', []) is None

    asset = cycle.social_assets_manager.get('token1_asset')
    assert asset.physical_storage_vector
    assert asset.physical_storage != old_storage[0]


def test_collect_water_asset_failed_param():
    try:
        cycle._collect_water_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_collect_water_asset_failed_unknown():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    try:
        cycle._collect_water_asset('token1_asset', [])
        assert False
    except Exception as e:
        if str(e.message).endswith('The asset is not in a location with a water sample event.'):
            assert True
        else:
            assert False




def test_take_photo_asset():
    cycle.steps[0]['photos'][0].active = True
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get('token1_asset').virtual_storage]
    action = [{'token': 'token1_asset', 'action': 'takePhoto', 'parameters': []}]
    results = cycle.execute_actions(action)
    asset = get_result_agent('token1_asset', results)

    assert asset.virtual_storage_vector
    assert asset.virtual_storage != old_storage


def test_take_photo_asset_failed_param():
    try:
        cycle._take_photo_asset('token_asset', [1])
        assert False
    except Exception as e:
        if str(e.message).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_take_photo_asset_failed_unknown():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    try:
        cycle._take_photo_asset('token1_asset', [])
        assert False
    except Exception as e:
        if str(e.message).endswith('The asset is not in a location with a photograph event.'):
            assert True
        else:
            assert False


@pytest.mark.dependency()
def test_take_photo():
    actions = [{'token': 'token4_agent', 'action': 'takePhoto', 'parameters': [1]}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action == 'takePhoto'
    assert agent.last_action_result != 'success'

    actions = [{'token': 'token1_asset', 'action': 'takePhoto', 'parameters': []}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token1_asset', results)
    assert agent.last_action == 'takePhoto'
    assert agent.last_action_result != 'success'

    cycle.steps[0]['photos'][0].active = True
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    old_storage = [cycle.agents_manager.get('token4_agent').virtual_storage]

    actions = [{'token': 'token4_agent', 'action': 'takePhoto', 'parameters': []}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action == 'takePhoto'
    assert agent.last_action_result == 'success'
    assert agent.virtual_storage_vector
    assert agent.virtual_storage != old_storage

@pytest.mark.dependency(depends=["test_take_photo"])
def test_analyze_photo():
    test_take_photo()
    actions = [{'token': 'token4_agent', 'action': 'analyzePhoto', 'parameters': [1]}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action == 'analyzePhoto'
    assert agent.last_action_result != 'success'

    actions = [{'token': 'token4_agent', 'action': 'analyzePhoto', 'parameters': []}]
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action_result == 'success'
    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity
    
    results = cycle.execute_actions(actions)
    agent = get_result_agent('token4_agent', results)
    assert agent.last_action_result != 'success'

@pytest.mark.dependency(depends=["test_take_photo_asset"])
def test_analyze_photo_asset():
    assert cycle._analyze_photo_asset('token1_asset', []) is None

    asset = cycle.social_assets_manager.get('token1_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_analyze_photo_asset_failed_param():
    try:
        cycle._analyze_photo_asset('token1_asset', [1])
        assert False
    except Exception as e:
        if str(e.message).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_analyze_photo_asset_failed_no_photos():
    try:
        cycle._analyze_photo_asset('token1_asset', [])
        assert False
    except Exception as e:
        if str(e.message).endswith('The asset has no photos to analyze.'):
            assert True
        else:
            assert False


# def test_search_social_asset_agent():
#     assert cycle._search_social_asset_agent('token1_agent', [1000]) is None

#     agent = cycle.agents_manager.get('token1_agent')

#     assert agent.social_assets


def test_search_social_asset_agent_failed_param():
    try:
        cycle._search_social_asset_agent('token_agent', [])
        assert False
    except Exception as e:
        if str(e.message).endswith('Wrong amount of parameters given.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_cdm():
    loc = cycle.cdm_location
    cycle.agents_manager.edit('token4_agent', 'location', [*loc])
    cycle.agents_manager.edit('token4_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token4_agent', 'physical_storage_vector', [Item(2, 'victim', 2)])
    cycle.agents_manager.edit('token4_agent', 'physical_storage', 10)
    action = [{'token': 'token4_agent', 'action': 'deliverPhysical', 'parameters': ['victim',1]}]
    results = cycle.execute_actions(action)
    agent = get_result_agent('token4_agent', results) 
    assert agent.last_action == 'deliverPhysical'
    assert agent.last_action_result == 'success'
    assert agent.physical_storage_vector == []
    


def test_deliver_physical():
    cycle.agents_manager.edit('token3_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token4_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'physical_storage_vector', [Item(2, 'victim', 2)])
    cycle.agents_manager.edit('token3_agent', 'physical_storage', 5)

    actions = [{'token': 'token3_agent', 'action': 'deliverPhysical', 'parameters': ['victim','token4_agent',1]}, {'token': 'token4_agent', 'action': 'receivePhysical', 'parameters': ['token3_agent']}]
    results = cycle.execute_actions(actions)
    agent3 = get_result_agent('token3_agent', results)    
    assert agent3.last_action == 'deliverPhysical'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector == []

    agent4 = get_result_agent('token4_agent', results)    
    assert agent4.last_action == 'receivePhysical'
    assert agent4.last_action_result == 'success'
    assert agent4.physical_storage_vector[0].identifier == 2
    assert agent4.physical_storage_vector[0].size == 2
    assert agent4.physical_storage_vector[0].type == 'victim'

def test_deliver_physical_agent_cdm_failed_less_param():
    try:
        cycle._deliver_physical_agent_cdm('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_cdm_failed_more_param():
    try:
        cycle._deliver_physical_agent_cdm('token4_agent', [1, 2, 3, 4])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_cdm_failed_location():
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    try:
        cycle._deliver_physical_agent_cdm('token4_agent', ['victim'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset_cdm():
    cycle.social_assets_manager.get('token1_asset').clear_physical_storage()
    cycle.steps[0]['water_samples'][0].active = True
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)
    cycle._collect_water_asset('token1_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)
    assert cycle._deliver_physical_asset_cdm('token1_asset', ['water_sample']) is None

    asset = cycle.social_assets_manager.get('token1_asset')

    assert not asset.physical_storage_vector
    assert asset.physical_storage == asset.physical_capacity


def test_deliver_physical_asset_agent():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token1_asset', 'physical_storage', 10)
    cycle.social_assets_manager.edit('token1_asset', 'physical_storage_vector', [Item(1, 'victim', 3)])
    assert cycle._deliver_physical_asset_agent('token1_asset', ['victim', 1, 'token4_agent']) is None


def test_deliver_physical_asset_cdm_failed_less_param():
    try:
        cycle._deliver_physical_asset_cdm('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset_cdm_failed_more_param():
    try:
        cycle._deliver_physical_asset_cdm('token4_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset_cdm_failed_location():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    try:
        cycle._deliver_physical_asset_cdm('token1_asset', ['water_sample'])
        assert False
    except Exception as e:
        if str(e.message).endswith('The social asset is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_cdm():
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    cycle.activate_step()
    cycle.current_step = 1
    cycle._take_photo_agent('token4_agent', [])

    loc = cycle.cdm_location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    assert cycle._deliver_virtual_agent_cdm('token4_agent', ['photo']) is None

    agent = cycle.agents_manager.get('token4_agent')

    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity

def test_match():
    actions = [{'token': 'token3_agent', 'action': 'deliverVirtual', 'parameters': ['photo','token5_agent',1]}, {'token': 'token4_agent', 'action': 'receiveVirtual', 'parameters': ['token3_agent']}]
    cycle.execute_actions(actions)
    
    assert cycle.agents_manager.get('token3_agent').last_action == 'deliverVirtual'
    assert cycle.agents_manager.get('token3_agent').last_action_result != 'success'   

    assert cycle.agents_manager.get('token4_agent').last_action == 'receiveVirtual'
    assert cycle.agents_manager.get('token4_agent').last_action_result != 'success'

def test_deliver_virtual():
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage', 10)

    # assert cycle._deliver_virtual_agent_agent('token3_agent', ['photo', 1, 'token4_agent']) is None
    actions = [{'token': 'token3_agent', 'action': 'deliverVirtual', 'parameters': ['photo','token4_agent',1]}, {'token': 'token4_agent', 'action': 'receiveVirtual', 'parameters': ['token3_agent']}]
    cycle.execute_actions(actions)
    
    assert cycle.agents_manager.get('token3_agent').last_action == 'deliverVirtual'
    assert cycle.agents_manager.get('token3_agent').last_action_result == 'success'
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector == []

    assert cycle.agents_manager.get('token4_agent').last_action == 'receiveVirtual'
    assert cycle.agents_manager.get('token4_agent').last_action_result == 'success'
    assert cycle.agents_manager.get('token4_agent').virtual_storage_vector[0].identifier == 4
    assert cycle.agents_manager.get('token4_agent').virtual_storage_vector[0].size == 1
    assert cycle.agents_manager.get('token4_agent').virtual_storage_vector[0].type == 'photo'

def test_deliver_virtual_parameters():
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage', 10)

    actions = [{'token': 'token3_agent', 'action': 'deliverVirtual', 'parameters': ['token4_agent',1]}, {'token': 'token4_agent', 'action': 'receiveVirtual', 'parameters': ['token3_agent']}]
    cycle.execute_actions(actions)
    
    assert cycle.agents_manager.get('token3_agent').last_action == 'deliverVirtual'
    assert cycle.agents_manager.get('token3_agent').last_action_result != 'success'
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].identifier == 4
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].size == 1
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].type == 'photo'    

    assert cycle.agents_manager.get('token4_agent').last_action == 'receiveVirtual'
    assert cycle.agents_manager.get('token4_agent').last_action_result != 'success'
    assert cycle.agents_manager.get('token4_agent').virtual_storage_vector == []

def test_deliver_virtual_constraints():
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage_vector', [Item(4, 'photo', 4)])
    cycle.agents_manager.edit('token4_agent', 'virtual_storage', 7)

    # assert cycle._deliver_virtual_agent_agent('token3_agent', ['photo', 1, 'token4_agent']) is None
    actions = [{'token': 'token3_agent', 'action': 'deliverVirtual', 'parameters': ['photo','token4_agent',2]}, {'token': 'token4_agent', 'action': 'receiveVirtual', 'parameters': ['token3_agent']}]
    cycle.execute_actions(actions)
    
    assert cycle.agents_manager.get('token3_agent').last_action == 'deliverVirtual'
    assert cycle.agents_manager.get('token3_agent').last_action_result != 'success'
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].identifier == 4
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].size == 4
    assert cycle.agents_manager.get('token3_agent').virtual_storage_vector[0].type == 'photo'    

    assert cycle.agents_manager.get('token4_agent').last_action == 'receiveVirtual'
    assert cycle.agents_manager.get('token4_agent').last_action_result != 'success'
    assert cycle.agents_manager.get('token4_agent').virtual_storage_vector == []


def test_deliver_virtual_agent_cdm_failed_less_param():
    try:
        cycle._deliver_virtual_agent_cdm('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_cdm_failed_more_param():
    try:
        cycle._deliver_virtual_agent_cdm('token4_agent', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_cdm_failed_location():
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    try:
        cycle._deliver_virtual_agent_cdm('token4_agent', ['photo'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_cdm():
    cycle.steps[0]['photos'][0].active = True
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)
    cycle._take_photo_asset('token1_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit('token1_asset', 'location', loc)
    assert cycle._deliver_virtual_asset_cdm('token1_asset', ['photo']) is None

    asset = cycle.social_assets_manager.get('token1_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_deliver_virtual_asset_agent():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token1_asset', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.social_assets_manager.edit('token1_asset', 'virtual_storage', 10)
    assert cycle._deliver_virtual_asset_agent('token1_asset', ['photo', 1, 'token4_agent']) is None


def test_deliver_virtual_asset_failed_less_param():
    try:
        cycle._deliver_virtual_asset_cdm('token1_asset', [])
        assert False
    except Exception as e:
        if str(e.message).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_more_param():
    try:
        cycle._deliver_virtual_asset_cdm('token1_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e.message).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_location():
    cycle.social_assets_manager.edit('token1_asset', 'location', [10, 10])
    try:
        cycle._deliver_virtual_asset_cdm('token1_asset', ['photo'])
        assert False
    except Exception as e:
        if str(e.message).endswith('The social asset is not located at the CDM.'):
            assert True
        else:
            assert False


def test_update_photos_state():
    identifiers = [photo.identifier for photo in cycle.steps[0]['photos']]
    cycle._update_photos_state(identifiers)

    for photo in cycle.steps[0]['photos']:
        assert photo.analyzed
        for victim in photo.victims:
            assert victim.active


def test_execute_agent_action():
    cycle.agents_manager.edit('token4_agent', 'carried', False)
    assert cycle._execute_agent_action('token4_agent', 'unknown', [])['message'] == 'Wrong action name given.'

    cycle.agents_manager.edit('token4_agent', 'is_active', False)
    assert cycle._execute_agent_action('token4_agent', 'pass', [])['message'] == 'Agent is not active.'
    cycle.agents_manager.edit('token4_agent', 'is_active', True)

    cycle.agents_manager.edit('token4_agent', 'carried', True)
    assert cycle._execute_agent_action('token4_agent', 'pass', [])[
               'message'] == 'Agent can not do any action while being carried.'
    cycle.agents_manager.edit('token4_agent', 'carried', False)

    assert not cycle._execute_agent_action('token4_agent', 'pass', [])['message']

    assert cycle._execute_agent_action('token4_agent', 'inactive', [])['message'] == 'Agent did not send any action.'

    cycle.agents_manager.edit('token4_agent', 'resources', [])
    assert cycle._execute_agent_action('token4_agent', 'charge', [])[
               'message'] == 'Agent does not have the abilities or resources to complete the action.'

    cycle.agents_manager.edit('token4_agent', 'resources', ['battery'])
    cycle.agents_manager.edit('token4_agent', 'location', cycle.cdm_location)
    assert not cycle._execute_agent_action('token4_agent', 'charge', [])['message']


def test_execute_asset_action():
    cycle.social_assets_manager.edit('token1_asset', 'carried', False)
    assert cycle._execute_asset_action('token1_asset', 'unknown', [])['message'] == 'Wrong action name given.'

    cycle.social_assets_manager.edit('token1_asset', 'is_active', False)
    assert cycle._execute_asset_action('token1_asset', 'pass', [])['message'] == 'Social asset is not active.'
    cycle.social_assets_manager.edit('token1_asset', 'is_active', True)

    cycle.social_assets_manager.edit('token1_asset', 'carried', True)
    assert cycle._execute_asset_action('token1_asset', 'pass', [])[
               'message'] == 'Social asset can not do any action while being carried.'
    cycle.social_assets_manager.edit('token1_asset', 'carried', False)

    assert not cycle._execute_asset_action('token1_asset', 'pass', [])['message']

    assert cycle._execute_asset_action('token1_asset', 'inactive', [])['message'] == 'Social asset did not send any action.'

    cycle.steps[0]['victims'][0].active = True
    cycle.social_assets_manager.edit('token1_asset', 'location', cycle.steps[0]['victims'][0].location)
    cycle.social_assets_manager.edit('token1_asset', 'physical_storage', 500)
    cycle.social_assets_manager.edit('token1_asset', 'abilities', ["carry"])
    cycle.social_assets_manager.edit('token1_asset', 'resources', ["strength"])

    assert cycle._execute_asset_action('token1_asset', 'rescueVictim', [])['message'] == ''

    cycle.social_assets_manager.edit('token1_asset', 'abilities', [])
    assert cycle._execute_asset_action('token1_asset', 'rescueVictim', [])[
               'message'] == 'Social asset does not have the abilities or resources to complete the action.'

def test_carry_agent():
    cycle.agents_manager.edit('token3_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])

    actions = [{'token': 'token3_agent', 'action': 'carry', 'parameters': ['token4_agent']}, {'token': 'token4_agent', 'action': 'getCarried', 'parameters': ['token3_agent']}]
    results = cycle.execute_actions(actions)
    agent3 = get_result_agent('token3_agent', results)    
    assert agent3.last_action == 'carry'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector != []
    agent4 = get_result_agent('token4_agent', results) 
    assert agent4.last_action == 'getCarried'
    assert agent4.last_action_result == 'success'
    assert agent4.carried == True

def test_deliver_agent():
    test_carry_agent()
    cycle.agents_manager.edit('token3_agent', 'location', [20, 20])

    actions = [{'token': 'token3_agent', 'action': 'deliverAgent', 'parameters': ['token4_agent']}, {'token': 'token4_agent', 'action': 'deliverRequest', 'parameters': ['token3_agent']}]
    results = cycle.execute_actions(actions)
    agent3 = get_result_agent('token3_agent', results)    
    assert agent3.last_action == 'deliverAgent'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector == []
    agent4 = get_result_agent('token4_agent', results) 
    assert agent4.last_action == 'deliverRequest'
    assert agent4.last_action_result == 'success'
    assert agent4.carried == False
    assert agent4.location == [20,20]

def test_execute_special_actions():
    cycle.execute_actions([{'token': 'token2_agent', 'action': 'searchSocialAsset', 'parameters': [50000]}])
    cycle.execute_actions([{'token': 'token2_agent', 'action': 'requestSocialAsset', 'parameters': [3]}])
    cycle.connect_social_asset('token2_agent', 'token2_asset')

    special_actions_list = [
        {'token': 'token_agent1', 'action': 'carry', 'parameters': ['token1_asset']},
        {'token': 'token1_asset', 'action': 'getCarried', 'parameters': ['token_agent1']},
        {'token': 'token2_agent', 'action': 'receiveVirtual', 'parameters': ['token1_asset1']},
        {'token': 'token_asset1', 'action': 'deliverVirtual', 'parameters': ['photo', 1, 'token2_agent']},
        {'token': 'token3_agent', 'action': 'deliverPhysical', 'parameters': ['water_sample', 1, 'token2_asset']},
        {'token': 'token2_asset', 'action': 'receivePhysical', 'parameters': ['token3_agent']},
    ]

    cycle.agents_manager.edit('token_agent1', 'carried', False)
    cycle.agents_manager.edit('token_agent1', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token_agent1', 'location', [10, 10])
    cycle.social_assets_manager.edit('token_asset', 'carried', False)
    cycle.social_assets_manager.edit('token_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token_asset1', 'carried', False)
    cycle.social_assets_manager.edit('token_asset1', 'location', [10, 10])
    cycle.social_assets_manager.edit('token_asset1', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.social_assets_manager.edit('token_asset1', 'virtual_storage', 50)
    cycle.agents_manager.edit('token3_agent', 'carried', False)
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'physical_storage_vector', [Item(1, 'water_sample', 4)])
    cycle.agents_manager.edit('token3_agent', 'physical_storage', 50)
    cycle.agents_manager.edit('token3_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'location', [10, 10])
    result = cycle.execute_actions(special_actions_list)[0]

    assert not result[0]['message']
    assert result[0]['agent'].last_action_result
    assert result[0]['agent'].last_action == 'carry'

    assert not result[1]['message']
    assert result[1]['social_asset'].last_action_result
    assert result[1]['social_asset'].last_action == 'getCarried'

    assert not result[2]['message']
    assert result[2]['agent'].last_action_result
    assert result[2]['agent'].last_action == 'receiveVirtual'

    assert not result[3]['message']
    assert result[3]['social_asset'].last_action_result
    assert result[3]['social_asset'].last_action == 'deliverVirtual'

    assert not result[4]['message']
    assert result[4]['agent'].last_action_result
    assert result[4]['agent'].last_action == 'deliverPhysical'

    assert not result[5]['message']
    assert result[5]['social_asset'].last_action_result
    assert result[5]['social_asset'].last_action == 'receivePhysical'


def test_execute_special_actions_failed_being_carried():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'carry', 'parameters': ['token2_agent']}
    ]

    cycle.agents_manager.edit('token2_agent', 'carried', True)
    cycle.social_assets_manager.edit('token2_asset', 'carried', True)
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'Agent can not do any action while being carried.'
    assert result[1]['message'] == 'Social asset can not do any action while being carried.'


def test_execute_special_actions_failed_abilities():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'carry', 'parameters': ['token2_agent']}
    ]
    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'abilities', [])
    cycle.social_assets_manager.edit('token2_asset', 'abilities', [])
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'Agent does not have the abilities or resources to complete the action.'
    assert result[1]['message'] == 'Social asset does not have the abilities or resources to complete the action.'


def test_execute_special_actions_failed_param():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': []},
        {'token': 'token2_asset', 'action': 'carry', 'parameters': [1, 2]}
    ]

    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token2_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'More or less than 1 parameter was given.'
    assert result[1]['message'] == 'More or less than 1 parameter was given.'

    special_actions_list = [
        {'token': 'token2_agent', 'action': 'getCarried', 'parameters': []},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': [1, 2]}
    ]

    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token2_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'More or less than 1 parameter was given.'
    assert result[1]['message'] == 'More or less than 1 parameter was given.'


def test_execute_special_actions_failed_no_other_get_carried():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token4_asset']},
        {'token': 'token2_asset', 'action': 'carry', 'parameters': ['token4_agent']}
    ]
    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token2_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'No other agent or social asset wants to be carried.'
    assert result[1]['message'] == 'No other agent or social asset wants to be carried.'


def test_execute_special_actions_failed_no_other_carry():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'getCarried', 'parameters': ['token4_asset']},
        {'token': 'token1_asset', 'action': 'getCarried', 'parameters': ['token4_agent']}
    ]
    result = cycle.execute_actions(special_actions_list)[0]
    assert result[0]['message'] == 'No other agent or social asset wants to carry.'
    assert result[1]['message'] == 'No other agent or social asset wants to carry.'


# def test_execute_actions():
#     actions_tokens_list = [
#         {'token': 'token1_agent', 'action': 'carry', 'parameters': ['token1_asset']},
#         {'token': 'token1_asset', 'action': 'getCarried', 'parameters': ['token1_agent']},
#         {'token': 'token2_agent', 'action': 'pass', 'parameters': []},
#         {'token': 'token2_asset', 'action': 'rescueVictim', 'parameters': []}
#     ]
#     cycle.agents_manager.edit('token1_agent', 'carried', False)
#     cycle.agents_manager.edit('token2_agent', 'carried', False)
#     cycle.social_assets_manager.edit('token1_asset', 'carried', False)
#     cycle.social_assets_manager.edit('token2_asset', 'carried', False)
#     cycle.steps[0]['victims'][1].active = True
#     cycle.social_assets_manager.edit('token2_asset', 'location', cycle.steps[0]['victims'][1].location)
#     result = cycle.execute_actions(actions_tokens_list)[0]

#     print(len(result))
#     for i in range(4):
#         assert not result[i]['message']

#     for i in range(4, 9):
#         assert result[i]['message'] == 'Agent did not send any action.' or\
#                result[i]['message'] == 'Social asset did not send any action.'


def test_restart():
    cycle.agents_manager.edit('token1_agent', 'carried', True)
    cycle.agents_manager.edit('token1_agent', 'is_active', False)
    cycle.social_assets_manager.edit('token1_asset', 'carried', True)
    cycle.social_assets_manager.edit('token1_asset', 'is_active', False)
    cycle.restart(config_json, False, False)
    assert not cycle.steps[0]['flood'].active
    assert cycle.current_step == 0
    assert not cycle.delivered_items
    assert not cycle.agents_manager.get('token2_agent').carried
    assert cycle.agents_manager.get('token2_agent').is_active
    assert len(cycle.social_assets_manager.get_tokens()) == 0


if __name__ == '__main__':
    test_connect_agent()
    test_connect_asset()
    test_disconnect_agent()
    test_disconnect_asset()
    test_get_agents_info()
    test_get_active_agents_info()
    test_get_assets_info()
    test_get_active_assets_info()
    test_get_step()
    test_activate_step()
    test_get_previous_steps()
    test_check_steps()
    test_update_steps()
    test_check_abilities_and_resources()
    test_charge()
    test_charge_failed_param()
    test_charge_failed_location()
    test_move_agent()
    test_move_agent_failed_facility()
    test_move_agent_failed_less_parameters()
    test_move_agent_failed_more_parameters()
    test_move_agent_failed_battery()
    test_move_agent_failed_unable()
    test_move_asset()
    test_move_asset_failed_facility()
    test_move_asset_failed_less_parameters()
    test_move_asset_failed_more_parameters()
    test_move_asset_failed_unable()
    test_rescue_victim_agent()
    test_rescue_victim_agent_failed_param()
    test_rescue_victim_agent_failed_unknown()
    test_rescue_victim_asset()
    test_rescue_victim_asset_failed_param()
    test_rescue_victim_asset_failed_unknown()
    test_collect_water_agent()
    test_collect_water_agent_failed_param()
    test_collect_water_agent_failed_unknown()
    test_collect_water_asset()
    test_collect_water_asset_failed_param()
    test_collect_water_asset_failed_unknown()
    test_take_photo_agent()
    test_take_photo_agent_failed_param()
    test_take_photo_agent_failed_unknown()
    test_take_photo_asset()
    test_take_photo_asset_failed_param()
    test_take_photo_asset_failed_unknown()
    test_analyze_photo_agent()
    test_analyze_photo_agent_failed_param()
    test_analyze_photo_agent_failed_no_photos()
    test_analyze_photo_asset()
    test_analyze_photo_asset_failed_param()
    test_analyze_photo_asset_failed_no_photos()
    test_search_social_asset_agent()
    test_deliver_physical_agent_cdm()
    test_deliver_physical_agent_agent()
    test_deliver_physical_agent_cdm_failed_less_param()
    test_deliver_physical_agent_cdm_failed_more_param()
    test_deliver_physical_agent_cdm_failed_more_param()
    test_deliver_physical_asset_cdm()
    test_deliver_physical_asset_agent()
    test_deliver_physical_asset_cdm_failed_less_param()
    test_deliver_physical_asset_cdm_failed_more_param()
    test_deliver_physical_asset_cdm_failed_location()
    test_deliver_virtual_agent_cdm()
    test_deliver_virtual_agent_agent()
    test_deliver_virtual_agent_cdm_failed_less_param()
    test_deliver_virtual_agent_cdm_failed_more_param()
    test_deliver_virtual_agent_cdm_failed_location()
    test_deliver_virtual_asset_cdm()
    test_deliver_virtual_asset_agent()
    test_deliver_virtual_asset_failed_less_param()
    test_deliver_virtual_asset_failed_more_param()
    test_deliver_virtual_asset_failed_location()
    test_update_photos_state()
    test_execute_agent_action()
    test_execute_asset_action()
    test_execute_special_actions()
    test_execute_special_actions_failed_being_carried()
    test_execute_special_actions_failed_param()
    test_execute_special_actions_failed_abilities()
    test_execute_special_actions_failed_no_other_carry()
    test_execute_special_actions_failed_no_other_get_carried()
    test_execute_actions()
    test_restart()
