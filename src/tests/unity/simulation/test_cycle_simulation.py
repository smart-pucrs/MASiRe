import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.cycle import Cycle

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
cycle = Cycle(config_json)


class Item:
    def __init__(self, size, type, identifier):
        self.size = size
        self.type = type
        self.identifier = identifier


def test_connect_agent():
    assert cycle.connect_agent('token_agent')


def test_connect_asset():
    assert cycle.connect_social_asset('token_asset')


def test_disconnect_agent():
    assert cycle.disconnect_agent('token_agent')


def test_disconnect_asset():
    assert cycle.disconnect_social_asset('token_asset')


def test_get_agents_info():
    assert len(cycle.get_agents_info()) == 1

    cycle.connect_agent('token_agent1')

    assert len(cycle.get_agents_info()) == 2


def test_get_active_agents_info():
    assert len(cycle.get_active_agents_info()) == 1


def test_get_assets_info():
    assert len(cycle.get_assets_info()) == 1

    cycle.connect_social_asset('token_asset1')
    assert len(cycle.get_assets_info()) == 2


def test_get_active_assets_info():
    assert len(cycle.get_active_assets_info()) == 1


def test_get_step():
    assert cycle.get_step()


def test_activate_step():
    old = cycle.get_step()
    assert not old['flood'].active

    cycle.activate_step()
    new = cycle.get_step()

    assert new['flood'].active


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
    old_period = cycle.steps[0]['flood'].period
    cycle.update_steps()
    new_period = cycle.steps[0]['flood'].period

    assert old_period != new_period


def test_nothing_just_setup_for_pytest():
    cycle.restart(config_json)
    for i in range(10):
        cycle.current_step = i
        cycle.activate_step()
        cycle.update_steps()


def test_check_abilities_and_resources():
    assert cycle._check_abilities_and_resources('token_agent', 'move')

    for i in range(1, 4):
        cycle.connect_agent(f'token{i + 1}_agent')

    cycle.connect_agent('agent_without_abilities')
    assert not cycle._check_abilities_and_resources('agent_without_abilities', 'move')

    cycle.connect_agent('agent_without_resources')
    assert not cycle._check_abilities_and_resources('agent_without_resources', 'charge')

    for i in range(1, 4):
        cycle.connect_social_asset(f'token{i + 1}_asset')

    cycle.connect_social_asset('asset_without_abilities')
    assert not cycle._check_abilities_and_resources('asset_without_abilities', 'move')

    cycle.connect_social_asset('asset_without_resources')
    assert not cycle._check_abilities_and_resources('asset_without_resources', 'charge')


def test_charge():
    loc = config_json['map']['centerLat'], config_json['map']['centerLon']
    cycle.agents_manager.edit('token_agent1', 'location', loc)
    assert cycle._charge_agent('token_agent1', []) is None


def test_charge_failed_param():
    try:
        cycle._charge_agent('token_agent1', ['parameter_given'])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_charge_failed_location():
    cycle.agents_manager.edit('token_agent1', 'location', [120, 120])
    try:
        cycle._charge_agent('token_agent1', [])
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

    assert cycle._move_agent('token3_agent', loc) is None
    assert cycle.agents_manager.get('token3_agent').route
    assert cycle.agents_manager.get('token3_agent').destination_distance
    old_dist = [cycle.agents_manager.get('token3_agent').destination_distance]

    cycle._move_agent('token3_agent', loc)
    cycle._move_agent('token3_agent', loc)

    loc = ['cdm']

    assert cycle._move_agent('token3_agent', loc) is None
    assert cycle.agents_manager.get('token3_agent').route
    assert cycle.agents_manager.get('token3_agent').destination_distance
    assert old_dist[0] != cycle.agents_manager.get('token3_agent').destination_distance


def test_move_agent_failed_facility():
    try:
        cycle._move_agent('token3_agent', ['unknown_facility'])
        assert False
    except Exception as e:
        if str(e).endswith('Unknown facility.'):
            assert True
        else:
            assert False


def test_move_agent_failed_less_parameters():
    try:
        cycle._move_agent('token3_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_move_agent_failed_more_parameters():
    try:
        cycle._move_agent('token3_agent', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_move_agent_failed_battery():
    cycle.agents_manager.edit('token3_agent', 'actual_battery', 0)
    try:
        cycle._move_agent('token3_agent', [10, 10])
        assert False
    except Exception as e:
        if str(e).endswith('Not enough battery to complete this step.'):
            assert True
        else:
            assert False


def test_move_agent_failed_unable():
    cycle.agents_manager.edit('agent_without_abilities', 'abilities', ['move'])
    cycle.agents_manager.edit('agent_without_abilities', 'location', [10, 10])
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].list_of_nodes[3])
    try:
        cycle._move_agent('agent_without_abilities', loc)
        assert False
    except Exception as e:
        if str(e).endswith('Agent is not capable of entering flood locations.'):
            assert True
        else:
            assert False


def test_move_asset():
    asset = cycle.social_assets_manager.get('token3_asset')
    loc = list(asset.location)
    loc[0] = loc[0] + 5
    loc[1] = loc[1] + 5

    assert cycle._move_asset('token3_asset', loc) is None
    assert cycle.social_assets_manager.get('token3_asset').route
    assert cycle.social_assets_manager.get('token3_asset').destination_distance
    old_dist = [cycle.social_assets_manager.get('token3_asset').destination_distance]

    while cycle.social_assets_manager.get('token3_asset').route[:-3]:
        cycle._move_asset('token3_asset', loc)

    loc = ['cdm']

    assert cycle._move_asset('token3_asset', loc) is None
    assert cycle.social_assets_manager.get('token3_asset').route
    assert cycle.social_assets_manager.get('token3_asset').destination_distance
    assert old_dist[0] != cycle.social_assets_manager.get('token3_asset').destination_distance


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
    cycle.social_assets_manager.edit('asset_without_abilities', 'abilities', ['move'])
    cycle.social_assets_manager.edit('asset_without_abilities', 'location', [10, 10])
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].list_of_nodes[3])
    try:
        cycle._move_asset('asset_without_abilities', loc)
        assert False
    except Exception as e:
        if str(e).endswith('Asset is not capable of entering flood locations.'):
            assert True
        else:
            assert False


def test_rescue_victim_agent():
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', victim_loc)

    old_storage = [cycle.agents_manager.get('token4_agent').physical_storage]
    assert cycle._rescue_victim_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get('token4_agent')
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
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.social_assets_manager.edit('token4_asset', 'location', victim_loc)

    old_storage = [cycle.social_assets_manager.get('token4_asset').physical_storage]
    assert cycle._rescue_victim_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get('token4_asset')
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
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    try:
        cycle._rescue_victim_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('No victim by the given location is known.'):
            assert True
        else:
            assert False


def test_collect_water_agent():
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)

    old_storage = [cycle.agents_manager.get('token4_agent').physical_storage]
    assert cycle._collect_water_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get('token4_agent')
    assert agent.physical_storage_vector
    assert agent.physical_storage != old_storage[0]


def test_collect_water_agent_failed_param():
    try:
        cycle._collect_water_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_collect_water_agent_failed_unknown():
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    try:
        cycle._collect_water_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not in a location with a water sample event.'):
            assert True
        else:
            assert False


def test_collect_water_asset():
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get('token4_asset').physical_storage]
    assert cycle._collect_water_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get('token4_asset')
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
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    try:
        cycle._collect_water_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset is not in a location with a water sample event.'):
            assert True
        else:
            assert False


def test_take_photo_agent():
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)

    old_storage = [cycle.agents_manager.get('token4_agent').virtual_storage]
    assert cycle._take_photo_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get('token4_agent')
    assert agent.virtual_storage_vector
    assert agent.virtual_storage != old_storage


def test_take_photo_agent_failed_param():
    try:
        cycle._take_photo_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_take_photo_agent_failed_unknown():
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    try:
        cycle._take_photo_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not in a location with a photograph event.'):
            assert True
        else:
            assert False


def test_take_photo_asset():
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get('token4_asset').virtual_storage]
    assert cycle._take_photo_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get('token4_asset')
    assert asset.virtual_storage_vector
    assert asset.virtual_storage != old_storage


def test_take_photo_asset_failed_param():
    try:
        cycle._take_photo_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_take_photo_asset_failed_unknown():
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    try:
        cycle._take_photo_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset is not in a location with a photograph event.'):
            assert True
        else:
            assert False


def test_analyze_photo_agent():
    assert cycle._analyze_photo_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get('token4_agent')

    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity


def test_analyze_photo_agent_failed_param():
    try:
        cycle._analyze_photo_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_analyze_photo_agent_failed_no_photos():
    try:
        cycle._analyze_photo_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent has no photos to analyze.'):
            assert True
        else:
            assert False


def test_analyze_photo_asset():
    assert cycle._analyze_photo_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get('token4_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_analyze_photo_asset_failed_param():
    try:
        cycle._analyze_photo_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_analyze_photo_asset_failed_no_photos():
    try:
        cycle._analyze_photo_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset has no photos to analyze.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent():
    assert cycle._search_social_asset_agent('token4_agent', ['doctor']) is None

    agent = cycle.agents_manager.get('token4_agent')

    assert agent.social_assets


def test_search_social_asset_agent_failed_param():
    try:
        cycle._search_social_asset_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Wrong amount of parameters given.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent_failed_purpose():
    try:
        cycle._search_social_asset_agent('token4_agent', ['unknown'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset found for the needed purposes.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent_failed_no_assets():
    cycle.social_assets_manager.social_assets.clear()
    cycle.social_assets_manager.capacities = cycle.social_assets_manager.generate_objects(config_json['map'],
                                                                                          config_json['socialAssets'])
    try:
        cycle._search_social_asset_agent('token4_agent', ['doctor'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset connected.'):
            assert True
        else:
            assert False

    for i in range(1, 4):
        cycle.connect_social_asset(f'token{i + 1}_asset')


def test_search_social_asset_asset():
    assert cycle._search_social_asset_asset('token4_asset', ['doctor']) is None

    asset = cycle.social_assets_manager.get('token4_asset')

    assert asset.social_assets


def test_search_social_asset_asset_failed_param():
    try:
        cycle._search_social_asset_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Wrong amount of parameters given.'):
            assert True
        else:
            assert False


def test_search_social_asset_asset_failed_purpose():
    try:
        cycle._search_social_asset_asset('token4_asset', ['unknown'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset found for the needed purposes.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_cdm():
    loc = cycle.cdm_location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    assert cycle._deliver_physical_agent_cdm('token4_agent', ['victim']) is None
    assert cycle._deliver_physical_agent_cdm('token4_agent', ['water_sample']) is None

    agent = cycle.agents_manager.get('token4_agent')

    assert not agent.physical_storage_vector
    assert agent.physical_storage == agent.physical_capacity


def test_deliver_physical_agent_agent():
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'physical_storage_vector', [Item(2, 'victim', 2)])
    cycle.agents_manager.edit('token3_agent', 'physical_storage', 5)
    assert cycle._deliver_physical_agent_agent('token3_agent', ['victim', 1, 'token4_agent']) is None


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
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)
    cycle._collect_water_asset('token4_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)
    assert cycle._deliver_physical_asset_cdm('token4_asset', ['water_sample']) is None

    asset = cycle.social_assets_manager.get('token4_asset')

    assert not asset.physical_storage_vector
    assert asset.physical_storage == asset.physical_capacity


def test_deliver_physical_asset_agent():
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token4_asset', 'physical_storage', 10)
    cycle.social_assets_manager.edit('token4_asset', 'physical_storage_vector', [Item(1, 'victim', 3)])
    assert cycle._deliver_physical_asset_agent('token4_asset', ['victim', 1, 'token4_agent']) is None


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
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    try:
        cycle._deliver_physical_asset_cdm('token4_asset', ['water_sample'])
        assert False
    except Exception as e:
        if str(e).endswith('The social asset is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_cdm():
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    cycle._take_photo_agent('token4_agent', [])

    loc = cycle.cdm_location
    cycle.agents_manager.edit('token4_agent', 'location', loc)
    assert cycle._deliver_virtual_agent_cdm('token4_agent', ['photo']) is None

    agent = cycle.agents_manager.get('token4_agent')

    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity


def test_deliver_virtual_agent_agent():
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.agents_manager.edit('token3_agent', 'virtual_storage', 10)
    assert cycle._deliver_virtual_agent_agent('token3_agent', ['photo', 1, 'token4_agent']) is None


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
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)
    cycle._take_photo_asset('token4_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit('token4_asset', 'location', loc)
    assert cycle._deliver_virtual_asset_cdm('token4_asset', ['photo']) is None

    asset = cycle.social_assets_manager.get('token4_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_deliver_virtual_asset_agent():
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token4_asset', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.social_assets_manager.edit('token4_asset', 'virtual_storage', 10)
    assert cycle._deliver_virtual_asset_agent('token4_asset', ['photo', 1, 'token4_agent']) is None


def test_deliver_virtual_asset_failed_less_param():
    try:
        cycle._deliver_virtual_asset_cdm('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_more_param():
    try:
        cycle._deliver_virtual_asset_cdm('token4_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_location():
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    try:
        cycle._deliver_virtual_asset_cdm('token4_asset', ['photo'])
        assert False
    except Exception as e:
        if str(e).endswith('The social asset is not located at the CDM.'):
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
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    assert cycle._execute_asset_action('token4_asset', 'unknown', [])['message'] == 'Wrong action name given.'

    cycle.social_assets_manager.edit('token4_asset', 'is_active', False)
    assert cycle._execute_asset_action('token4_asset', 'pass', [])['message'] == 'Social asset is not active.'
    cycle.social_assets_manager.edit('token4_asset', 'is_active', True)

    cycle.social_assets_manager.edit('token4_asset', 'carried', True)
    assert cycle._execute_asset_action('token4_asset', 'pass', [])[
               'message'] == 'Social asset can not do any action while being carried.'
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)

    assert not cycle._execute_asset_action('token4_asset', 'pass', [])['message']

    assert cycle._execute_asset_action('token4_asset', 'inactive', [])['message'] == 'Social asset did not send any action.'

    cycle.social_assets_manager.edit('token4_asset', 'location', cycle.steps[0]['victims'][0].location)
    cycle.social_assets_manager.edit('token4_asset', 'physical_storage', 500)
    assert cycle._execute_asset_action('token4_asset', 'rescueVictim', [])['message'] == ''

    cycle.social_assets_manager.edit('token4_asset', 'abilities', [])
    assert cycle._execute_asset_action('token4_asset', 'rescueVictim', [])[
               'message'] == 'Social asset does not have the abilities or resources to complete the action.'


def test_execute_special_actions():
    special_actions_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': ['token2_agent']},
        {'token': 'token3_agent', 'action': 'receiveVirtual', 'parameters': ['token3_asset']},
        {'token': 'token3_asset', 'action': 'deliverVirtual', 'parameters': ['photo', 1, 'token3_agent']},
        {'token': 'token4_agent', 'action': 'deliverPhysical', 'parameters': ['water_sample', 1, 'token4_asset']},
        {'token': 'token4_asset', 'action': 'receivePhysical', 'parameters': ['token4_agent']},
    ]

    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.agents_manager.edit('token2_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.agents_manager.edit('token2_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'location', [10, 10])
    cycle.agents_manager.edit('token3_agent', 'carried', False)
    cycle.agents_manager.edit('token3_agent', 'location', [10, 10])
    cycle.social_assets_manager.edit('token3_asset', 'carried', False)
    cycle.social_assets_manager.edit('token3_asset', 'location', [10, 10])
    cycle.social_assets_manager.edit('token3_asset', 'virtual_storage_vector', [Item(1, 'photo', 4)])
    cycle.social_assets_manager.edit('token3_asset', 'virtual_storage', 50)
    cycle.agents_manager.edit('token4_agent', 'carried', False)
    cycle.agents_manager.edit('token4_agent', 'location', [10, 10])
    cycle.agents_manager.edit('token4_agent', 'physical_storage_vector', [Item(1, 'water_sample', 4)])
    cycle.agents_manager.edit('token4_agent', 'physical_storage', 50)
    cycle.agents_manager.edit('token4_agent', 'abilities', ["carry", "physicalCapacity"])
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    cycle.social_assets_manager.edit('token4_asset', 'location', [10, 10])
    result = cycle.execute_actions(special_actions_list)
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
        {'token': 'token4_agent', 'action': 'carry', 'parameters': ['token4_asset']},
        {'token': 'token4_asset', 'action': 'carry', 'parameters': ['token4_agent']}
    ]

    cycle.agents_manager.edit('token4_agent', 'carried', True)
    cycle.social_assets_manager.edit('token4_asset', 'carried', True)
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'Agent can not do any action while being carried.'
    assert result[1]['message'] == 'Social asset can not do any action while being carried.'


def test_execute_special_actions_failed_abilities():
    special_actions_list = [
        {'token': 'token4_agent', 'action': 'carry', 'parameters': ['token4_asset']},
        {'token': 'token4_asset', 'action': 'carry', 'parameters': ['token4_agent']}
    ]
    cycle.agents_manager.edit('token4_agent', 'carried', False)
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    cycle.agents_manager.edit('token4_agent', 'abilities', [])
    cycle.social_assets_manager.edit('token4_asset', 'abilities', [])
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'Agent does not have the abilities or resources to complete the action.'
    assert result[1]['message'] == 'Social asset does not have the abilities or resources to complete the action.'


def test_execute_special_actions_failed_param():
    special_actions_list = [
        {'token': 'token4_agent', 'action': 'carry', 'parameters': []},
        {'token': 'token4_asset', 'action': 'carry', 'parameters': [1, 2]}
    ]

    cycle.agents_manager.edit('token4_agent', 'carried', False)
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    cycle.agents_manager.edit('token4_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token4_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'More or less than 1 parameter was given.'
    assert result[1]['message'] == 'More or less than 1 parameter was given.'

    special_actions_list = [
        {'token': 'token4_agent', 'action': 'getCarried', 'parameters': []},
        {'token': 'token4_asset', 'action': 'getCarried', 'parameters': [1, 2]}
    ]

    cycle.agents_manager.edit('token4_agent', 'carried', False)
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    cycle.agents_manager.edit('token4_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token4_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'More or less than 1 parameter was given.'
    assert result[1]['message'] == 'More or less than 1 parameter was given.'


def test_execute_special_actions_failed_no_other_get_carried():
    special_actions_list = [
        {'token': 'token4_agent', 'action': 'carry', 'parameters': ['token4_asset']},
        {'token': 'token4_asset', 'action': 'carry', 'parameters': ['token4_agent']}
    ]
    cycle.agents_manager.edit('token4_agent', 'carried', False)
    cycle.social_assets_manager.edit('token4_asset', 'carried', False)
    cycle.agents_manager.edit('token4_agent', 'abilities', ['carry', 'physicalCapacity'])
    cycle.social_assets_manager.edit('token4_asset', 'abilities', ['carry', 'physicalCapacity'])
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'No other agent or social asset wants to be carried.'
    assert result[1]['message'] == 'No other agent or social asset wants to be carried.'


def test_execute_special_actions_failed_no_other_carry():
    special_actions_list = [
        {'token': 'token4_agent', 'action': 'getCarried', 'parameters': ['token4_asset']},
        {'token': 'token4_asset', 'action': 'getCarried', 'parameters': ['token4_agent']}
    ]
    result = cycle.execute_actions(special_actions_list)
    assert result[0]['message'] == 'No other agent or social asset wants to carry.'
    assert result[1]['message'] == 'No other agent or social asset wants to carry.'


def test_execute_actions():
    actions_tokens_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': ['token2_agent']},
        {'token': 'token3_agent', 'action': 'pass', 'parameters': []},
        {'token': 'token3_asset', 'action': 'rescueVictim', 'parameters': []}
    ]
    cycle.agents_manager.edit('token2_agent', 'carried', False)
    cycle.agents_manager.edit('token3_agent', 'carried', False)
    cycle.social_assets_manager.edit('token2_asset', 'carried', False)
    cycle.social_assets_manager.edit('token3_asset', 'carried', False)
    cycle.social_assets_manager.edit('token3_asset', 'location', cycle.steps[0]['victims'][1].location)
    result = cycle.execute_actions(actions_tokens_list)

    for i in range(4):
        assert not result[i]['message']

    for i in range(4, 9):
        assert result[i]['message'] == 'Agent did not send any action.'

    assert result[9]['message'] == 'Social asset did not send any action.'


def test_restart():
    cycle.agents_manager.edit('token4_agent', 'carried', True)
    cycle.agents_manager.edit('token4_agent', 'is_active', False)
    cycle.social_assets_manager.edit('token4_asset', 'carried', True)
    cycle.social_assets_manager.edit('token4_asset', 'is_active', False)
    cycle.restart(config_json)
    assert not cycle.steps[0]['flood'].active
    assert cycle.current_step == 0
    assert not cycle.delivered_items
    assert not cycle.agents_manager.get('token4_agent').carried
    assert cycle.agents_manager.get('token4_agent').is_active
    assert not cycle.social_assets_manager.get('token4_asset').carried
    assert cycle.social_assets_manager.get('token4_asset').is_active


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
    test_nothing_just_setup_for_pytest()
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
    test_search_social_asset_agent_failed_param()
    test_search_social_asset_agent_failed_purpose()
    test_search_social_asset_agent_failed_no_assets()
    test_search_social_asset_asset()
    test_search_social_asset_asset_failed_param()
    test_search_social_asset_asset_failed_purpose()
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
