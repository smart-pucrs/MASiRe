import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.agents_manager import AgentsManager

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
cdm_loc = config_json['map']['centerLat'], config_json['map']['centerLon']
manager = AgentsManager(config_json['agents'], cdm_loc)


class Item:
    def __init__(self, size):
        self.type = 'item'
        self.size = size


def test_connect_agent():
    assert manager.connect('token')
    assert len(manager.get_tokens()) == 1
    assert manager.get('token') is not None


def test_disconnect_agent():
    assert manager.disconnect('token')
    assert not manager.get('token').is_active


def test_add_physical_to_active_agent():
    assert manager.connect('token1')
    assert manager.add_physical('token1', Item(10)) is None


def test_add_physical_to_inactive_agent():
    try:
        manager.add_physical('token', Item(10))
        assert False

    except Exception as e:
        if str(e).endswith('The agent does not have enough physical storage.'):
            assert True
        else:
            assert False


def test_add_physical_to_no_existing_agent():
    try:
        manager.add_physical('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_add_virtual_to_active_agent():
    assert manager.add_virtual('token1', Item(10)) is None


def test_add_virtual_to_inactive_agent():
    try:
        manager.add_virtual('token', Item(10))
        assert False

    except Exception as e:
        if str(e).endswith('The agent does not have enough physical storage.'):
            assert True
        else:
            assert False


def test_add_virtual_to_no_existing_agent():
    try:
        manager.add_virtual('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_add_asset_to_active_agent():
    assert manager.add('token1', Item(10)) is None


def test_add_asset_to_inactive_agent():
    assert manager.add('token', Item(10)) is None


def test_add_asset_to_no_existing_agent():
    try:
        manager.add('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_charge_agent():
    assert manager.charge('token1') is None


def test_discharge_agent():
    assert manager.discharge('token1') is None


def test_get_agent():
    active_agent = manager.get('token1')
    inactive_agent = manager.get('token')
    non_existent = manager.get('token2')
    assert active_agent.is_active
    assert not inactive_agent.is_active
    assert non_existent is None


def test_get_tokens():
    tokens = manager.get_tokens()
    assert len(tokens) == 1
    assert tokens[0] == 'token1'


def test_get_agents_info():
    agents_infos = manager.get_info()

    assert len(agents_infos) == 2
    assert not agents_infos[0].is_active
    assert agents_infos[1].is_active


def test_get_active_agents_info():
    agents_infos = manager.get_active_info()

    assert len(agents_infos) == 1
    assert agents_infos[0].is_active


def test_deliver_physical():
    assert manager.deliver_physical('token1', 'item')
    try:
        manager.deliver_physical('token1', 'item')
        assert False
    except Exception as e:
        if str(e).endswith('The agent has no physical items to deliver.'):
            assert True

        else:
            assert False


def test_deliver_virtual():
    assert manager.deliver_virtual('token1', 'item')
    try:
        manager.deliver_virtual('token1', 'item')
        assert False
    except Exception as e:
        if str(e).endswith('The agent has no virtual items to deliver.'):
            assert True

        else:
            assert False


def test_edit_agent():
    manager.edit('token1', 'route', [(10, 10)])
    assert manager.get('token1').route


def test_update_agent_location():
    manager.update_location('token1')
    assert manager.get('token1').location == (10, 10)


def test_clear_agent_physical_storage():
    for i in range(5):
        manager.add_physical('token1', Item(1))

    manager.clear_physical_storage('token1')
    assert not manager.get('token1').physical_storage_vector


def test_clear_agent_virtual_storage():
    for i in range(5):
        manager.add_virtual('token1', Item(1))

    manager.clear_virtual_storage('token1')
    assert not manager.get('token1').virtual_storage_vector


def test_restart():
    manager.restart(config_json['agents'], cdm_loc)
    assert len(manager.get_tokens()) == 2
    assert manager.get('token').is_active
    assert manager.get('token1').is_active


def test_generate_roles():
    roles = manager.generate_roles(config_json['agents'])
    for role in roles:
        if getattr(role, 'name') != 'drone' and getattr(role, 'name') != 'boat' and getattr(role, 'name') != 'car':
            assert False

        if getattr(role, 'size') != 30:
            assert False

        if getattr(role, 'battery') != 20:
            assert False

        if getattr(role, 'speed') != 7:
            assert False

    assert True


if __name__ == '__main__':

    test_connect_agent()
    test_disconnect_agent()
    test_add_physical_to_active_agent()
    test_add_physical_to_inactive_agent()
    test_add_physical_to_no_existing_agent()
    test_add_virtual_to_active_agent()
    test_add_virtual_to_inactive_agent()
    test_add_virtual_to_no_existing_agent()
    test_add_asset_to_active_agent()
    test_add_asset_to_inactive_agent()
    test_add_asset_to_no_existing_agent()
    test_charge_agent()
    test_discharge_agent()
    test_get_agent()
    test_get_tokens()
    test_get_agents_info()
    test_get_active_agents_info()
    test_deliver_physical()
    test_deliver_virtual()
    test_edit_agent()
    test_update_agent_location()
    test_clear_agent_physical_storage()
    test_clear_agent_virtual_storage()
    test_restart()
    test_generate_roles()