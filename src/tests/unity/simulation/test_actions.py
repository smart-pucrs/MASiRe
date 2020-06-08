import copy
import json
import sys
import pathlib
import pytest

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

class Item:
    def __init__(self, size, type, identifier):
        self.size = size
        self.type = type
        self.identifier = identifier

@pytest.fixture
def game_state():
    from src.execution.simulation_engine.simulation_helpers.cycle import Cycle
    config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
    config_json = json.load(open(config_path, 'r'))
    return Cycle(config_json, False, False)
def create_agent(game_state, token):
    game_state.connect_agent(token)
    return game_state.agents_manager.get(token)
def create_asset(game_state, agent, token):
    game_state.execute_actions([{'token': agent.token, 'action': 'searchSocialAsset', 'parameters': [1000]}])
    game_state.execute_actions([{'token': agent.token, 'action': 'requestSocialAsset', 'parameters': [0]}])
    game_state.connect_social_asset(agent.token, token)
    return game_state.agents_manager.get(token)
@pytest.fixture
def agent1(game_state):
    return create_agent(game_state,'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiYWdlbnRfNyJ9.OC3ApeMvjLXturADTbqoSJjaA6mmcQm_X-fijdGZ7aQ')
@pytest.fixture
def agent2(game_state):
    return create_agent(game_state,'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiYWdlbnRfNCJ9.A4m9XNqb4OMDo5vQ1TWozZeFtyhXqgdQ-3dkd2B15yo')
@pytest.fixture
def agent3(game_state):
    return create_agent(game_state,'token3_agent')
@pytest.fixture
def agent4(game_state):
    return create_agent(game_state,'token4_agent')
@pytest.fixture
def asset1(game_state, agent1):
    return create_asset(game_state, agent1, 'token1_asset')
@pytest.fixture
def asset2(game_state, agent2):
    return create_asset(game_state, agent2, 'token2_asset')

def test_asset_connection(game_state, agent1):
    agents, req = game_state.execute_actions([{'token': agent1.token, 'action': 'searchSocialAsset', 'parameters': [1000]}])
    assert req == []
    agents, req = game_state.execute_actions([{'token': agent1.token, 'action': 'requestSocialAsset', 'parameters': [0]}])
    assert req[0] == agent1.token

def test_charge_facility(game_state, agent1):
    actions = [{'token': agent1.token, 'action': 'charge', 'parameters': []}]
    agent1.actual_battery -= 1
    agent1.location = [10,10]
    game_state.execute_actions(actions)
    assert agent1.last_action_result != 'success'

    agent1.location = game_state.cdm_location
    game_state.execute_actions(actions)
    assert agent1.actual_battery == agent1.max_charge

def test_charge_any_place(game_state, agent1):
    agent1.actual_battery -= 1

    actions = [{'token': agent1.token, 'action': 'charge', 'parameters': []}]
    game_state.execute_actions(actions)
    assert agent1.actual_battery == agent1.max_charge


def test_move_agent(game_state, agent1):
    agent = agent1
    loc = list(agent.location)
    loc[0] = loc[0] + 5
    loc[1] = loc[1] + 5
    old_location = agent.location
    actions = [{'token': agent.token, 'action': 'move', 'parameters': [*loc]}]
    game_state.execute_actions(actions)
    assert agent.last_action == 'move'
    assert agent.last_action_result == 'success'
    assert agent.location != old_location
    assert agent.route != []
    assert agent.destination_distance
    old_dist = [agent.destination_distance]

    game_state.execute_actions(actions)
    game_state.execute_actions(actions)

    game_state.execute_actions([{'token': agent.token, 'action': 'move', 'parameters': ['unknown_facility']}])
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

    game_state.execute_actions([{'token': agent.token, 'action': 'move', 'parameters': []}])
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

    loc = ['cdm']
    game_state.execute_actions([{'token': agent.token, 'action': 'move', 'parameters': [*loc]}])
    assert agent.last_action == 'move'
    assert agent.last_action_result == 'success'

    agent.actual_battery = 0
    game_state.execute_actions([{'token': agent.token, 'action': 'move', 'parameters': [*loc]}])
    assert agent.last_action == 'move'
    assert agent.last_action_result != 'success'

def test_move_cannot_enter_event(game_state, agent1):
    game_state.steps[0]['flood'].active = True
    game_state.map.movement_restrictions['groundMovement'] = 100
    agent1.abilities = ['groundMovement']
    agent1.location = [10, 10]    
    loc = game_state.map.get_node_coord(game_state.steps[0]['flood'].nodes[3])
    action = [{'token': agent1.token, 'action': 'move', 'parameters': [*loc]}]
    game_state.execute_actions(action)
    assert agent1.last_action == 'move'
    assert agent1.last_action_result != 'success'
    game_state.map.movement_restrictions['groundMovement'] = 70

def test_move_until_reach_destination(game_state, agent1):
    game_state.steps[0]['flood'].active = True
    agent1.abilities = ['groundMovement']
    agent1.location = [10, 10]    
    loc = [game_state.steps[0]['flood'].dimension['location'][0]+0.001, game_state.steps[0]['flood'].dimension['location'][1]]
    action = [{'token': agent1.token, 'action': 'move', 'parameters': [*loc]}]
    old_distance = 0
    while agent1.location[0] != loc[0] and agent1.location[1] != loc[1]:
        game_state.execute_actions(action)
        assert agent1.destination_distance != old_distance
        if agent1.actual_battery < 10:
            agent1.actual_battery = agent1.max_charge
        old_distance = agent1.destination_distance
    assert agent1.last_action == 'move'
    assert agent1.last_action_result == 'success'
    assert agent1.route == []
    assert agent1.destination_distance == 0

def test_move_change_route_when_enter_event(game_state, agent1):
    game_state.steps[0]['flood'].active = True
    agent1.abilities = ['groundMovement']
    agent1.location = game_state.cdm_location 
    loc = [game_state.steps[0]['flood'].dimension['location'][0]+0.001, game_state.steps[0]['flood'].dimension['location'][1]]
    action = [{'token': agent1.token, 'action': 'move', 'parameters': [*loc]}]
    game_state.map.movement_restrictions['groundMovement'] = 10
    game_state.execute_actions(action)
    previous_route = copy.deepcopy(agent1.route)
    for i in range(5):
        game_state.steps[0]['flood'].update_state()
    game_state.map.movement_restrictions['groundMovement'] = 90
    route_updated = False
    while agent1.route != []:
        game_state.execute_actions(action)
        previous_route.pop(0)
        if agent1.actual_battery < 10:
            agent1.actual_battery = agent1.max_charge
        if (len(previous_route) != len(agent1.route)):
            route_updated = True
            break
    assert route_updated

def test_move_unable(game_state, asset1):
    asset1.abilities = ['hybridMovement']
    asset1.location = [10, 10]
    game_state.map.movement_restrictions['groundMovement'] = 100
    loc = game_state.map.get_node_coord(game_state.steps[0]['flood'].nodes[3])

    action = [{'token': asset1.token, 'action': 'move', 'parameters': [*loc]}]
    game_state.execute_actions(action)
    assert asset1.last_action == 'move'
    assert asset1.last_action_result != 'success'

def test_rescue_victim_agent(game_state, agent1):
    game_state.steps[0]['victims'][0].active = True
    old_storage = [agent1.physical_storage]
    action = [{'token': agent1.token, 'action': 'rescueVictim', 'parameters': []}]
    
    agent1.location = [10,10]
    game_state.execute_actions(action)
    assert agent1.last_action == 'rescueVictim'
    assert agent1.last_action_result != 'success'

    agent1.location = game_state.steps[0]['victims'][0].location 
    game_state.execute_actions(action)
    assert agent1.physical_storage_vector
    assert agent1.physical_storage != old_storage[0]

def test_collect_water(game_state, agent4):
    game_state.steps[0]['water_samples'][0].active = True
    loc = game_state.steps[0]['water_samples'][0].location
    agent4.location = loc

    actions = [{'token': 'token4_agent', 'action': 'collectWater', 'parameters': [1]}]
    game_state.execute_actions(actions)
    assert agent4.last_action == 'collectWater'
    assert agent4.last_action_result != 'success'

    actions = [{'token': 'token4_agent', 'action': 'collectWater', 'parameters': []}]
    game_state.execute_actions(actions)
    assert agent4.last_action == 'collectWater'
    assert agent4.last_action_result == 'success'

def test_collect_water_failed_unknown(game_state, agent1):
    agent1.location = [10, 10]
    actions = [{'token': agent1.token, 'action': 'collectWater', 'parameters': []}]
    game_state.execute_actions(actions)
    assert agent1.last_action == 'collectWater'
    assert agent1.last_action_result != 'success'

@pytest.mark.dependency()
def test_take_photo(game_state, agent4, asset1):
    actions = [{'token': agent4.token, 'action': 'takePhoto', 'parameters': [1]}]
    game_state.execute_actions(actions)
    assert agent4.last_action == 'takePhoto'
    assert agent4.last_action_result != 'success'

    actions = [{'token': asset1.token, 'action': 'takePhoto', 'parameters': []}]
    game_state.execute_actions(actions)
    assert asset1.last_action == 'takePhoto'
    assert asset1.last_action_result != 'success'

    game_state.steps[0]['photos'][0].active = True
    agent4.location = game_state.steps[0]['photos'][0].location
    old_storage = [agent4.virtual_storage]

    actions = [{'token': agent4.token, 'action': 'takePhoto', 'parameters': []}]
    game_state.execute_actions(actions)
    assert agent4.last_action == 'takePhoto'
    assert agent4.last_action_result == 'success'
    assert agent4.virtual_storage_vector
    assert agent4.virtual_storage != old_storage

@pytest.mark.dependency(depends=["test_take_photo"])
def test_analyze_photo(game_state, agent4, asset1):
    test_take_photo(game_state, agent4, asset1)
    actions = [{'token': agent4.token, 'action': 'analyzePhoto', 'parameters': [1]}]
    game_state.execute_actions(actions)
    assert agent4.last_action == 'analyzePhoto'
    assert agent4.last_action_result != 'success'

    actions = [{'token': agent4.token, 'action': 'analyzePhoto', 'parameters': []}]
    game_state.execute_actions(actions)
    assert agent4.last_action_result == 'success'
    assert not agent4.virtual_storage_vector
    assert agent4.virtual_storage == agent4.virtual_capacity
    
    game_state.execute_actions(actions)
    assert agent4.last_action_result != 'success'

def test_physical_facility(game_state, agent1):
    agent1.location = [10,10]
    agent1.abilities = ["carry", "physicalCapacity"]
    agent1.physical_storage_vector = [Item(2, 'victim', 2)]
    agent1.physical_storage = 10

    action = [{'token': agent1.token, 'action': 'deliverPhysical', 'parameters': ['victim',1]}]
    game_state.execute_actions(action)
    assert agent1.last_action == 'deliverPhysical'
    assert agent1.last_action_result != 'success'

    agent1.location = [*game_state.cdm_location]
    game_state.execute_actions(action)
    assert agent1.last_action_result == 'success'
    assert agent1.physical_storage_vector == []
    


def test_physical(game_state, agent3, agent4):
    agent3.abilities = ["carry", "physicalCapacity"]
    agent4.abilities = ["carry", "physicalCapacity"]
    agent3.location = [10, 10]
    agent4.location = [10, 10]
    agent3.physical_storage_vector = [Item(2, 'victim', 2)]
    agent3.physical_storage = 5

    actions = [{'token': agent3.token, 'action': 'deliverPhysical', 'parameters': [agent4.token,'victim',1]}, {'token': agent4.token, 'action': 'receivePhysical', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions)
    assert agent3.last_action == 'deliverPhysical'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector == []
    
    assert agent4.last_action == 'receivePhysical'
    assert agent4.last_action_result == 'success'
    assert agent4.physical_storage_vector[0].identifier == 2
    assert agent4.physical_storage_vector[0].size == 2
    assert agent4.physical_storage_vector[0].type == 'victim'

def test_match(game_state, agent3, agent4):
    actions = [{'token': agent3.token, 'action': 'deliverVirtual', 'parameters': ['photo','some_token',1]}, {'token': agent4.token, 'action': 'receiveVirtual', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions)
    assert agent3.last_action == 'deliverVirtual'
    assert agent3.last_action_result != 'success'   
    assert agent4.last_action == 'receiveVirtual'
    assert agent4.last_action_result != 'success'

def test_virtual(game_state, agent1, agent2):
    agent1.virtual_storage_vector = [Item(1, 'photo', 4)]
    agent1.virtual_storage = 10

    actions = [{'token': agent1.token, 'action': 'deliverVirtual', 'parameters': [agent2.token,'photo',1]}, {'token': agent2.token, 'action': 'receiveVirtual', 'parameters': [agent1.token]}]
    game_state.execute_actions(actions)
    
    assert agent1.last_action == 'deliverVirtual'
    assert agent1.last_action_result == 'success'
    assert agent1.virtual_storage_vector == []

    assert agent2.last_action == 'receiveVirtual'
    assert agent2.last_action_result == 'success'
    assert agent2.virtual_storage_vector[0].identifier == 4
    assert agent2.virtual_storage_vector[0].size == 1
    assert agent2.virtual_storage_vector[0].type == 'photo'

def test_virtual_parameters(game_state, agent3, agent4):
    agent3.location = [10, 10]
    agent4.location = [10, 10]
    agent3.virtual_storage_vector = [Item(1, 'photo', 4)]
    agent3.virtual_storage = 10

    actions = [{'token': agent3.token, 'action': 'deliverVirtual', 'parameters': [agent4.token,1]}, {'token': agent4.token, 'action': 'receiveVirtual', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions) 

    assert agent3.last_action == 'deliverVirtual'
    assert agent3.last_action_result != 'success'
    assert agent3.virtual_storage_vector[0].identifier == 4
    assert agent3.virtual_storage_vector[0].size == 1
    assert agent3.virtual_storage_vector[0].type == 'photo'    
    assert agent4.last_action == 'receiveVirtual'
    assert agent4.last_action_result != 'success'
    assert agent4.virtual_storage_vector == []

def test_virtual_constraints(game_state, agent3, agent4):
    agent3.location = [10, 10]
    agent4.location = [10, 10]
    agent3.virtual_storage_vector = [Item(4, 'photo', 4)]
    agent4.virtual_storage = 7

    actions = [{'token': agent3.token, 'action': 'deliverVirtual', 'parameters': ['photo',agent4.token,2]}, {'token': agent4.token, 'action': 'receiveVirtual', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions)
    
    assert agent3.last_action == 'deliverVirtual'
    assert agent3.last_action_result != 'success'
    assert agent3.virtual_storage_vector[0].identifier == 4
    assert agent3.virtual_storage_vector[0].size == 4
    assert agent3.virtual_storage_vector[0].type == 'photo'    

    assert agent4.last_action == 'receiveVirtual'
    assert agent4.last_action_result != 'success'
    assert agent4.virtual_storage_vector == []

def test_carry_agent(game_state, agent3, agent1):
    agent3.abilities = ["carry", "physicalCapacity"]
    agent3.location = [10, 10]
    agent1.location = [10, 10]

    actions = [{'token': agent3.token, 'action': 'carry', 'parameters': [agent1.token]}, {'token': agent1.token, 'action': 'getCarried', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions)
    assert agent3.last_action == 'carry'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector != []

    assert agent1.last_action == 'getCarried'
    assert agent1.last_action_result == 'success'
    assert agent1.carried == True

def test_deliver_agent(game_state, agent3, agent1):
    test_carry_agent(game_state, agent3, agent1)
    agent3.location = [20, 20]
    actions = [{'token': agent3.token, 'action': 'deliverAgent', 'parameters': [agent1.token]}, {'token': agent1.token, 'action': 'deliverRequest', 'parameters': [agent3.token]}]
    game_state.execute_actions(actions)  
    assert agent3.last_action == 'deliverAgent'
    assert agent3.last_action_result == 'success'
    assert agent3.physical_storage_vector == []
    assert agent1.last_action == 'deliverRequest'
    assert agent1.last_action_result == 'success'
    assert agent1.carried == False
    assert agent1.location == [20,20]
