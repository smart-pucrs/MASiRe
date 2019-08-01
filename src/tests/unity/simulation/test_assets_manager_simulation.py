import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.social_assets_manager import SocialAssetsManager

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
manager = SocialAssetsManager(config_json['map'], config_json['socialAssets'])


class Item:
    def __init__(self, size):
        self.type = 'item'
        self.size = size


def test_connect_asset():
    assert manager.connect('token')
    assert len(manager.get_tokens()) == 1


def test_disconnect_asset():
    assert manager.disconnect('token')
    assert not manager.get('token').is_active


def test_add_physical_to_active_asset():
    assert manager.connect('token1')
    assert manager.add_physical('token1', Item(10)) is None


def test_add_physical_to_inactive_asset():
    try:
        manager.add_physical('token', Item(10))
        assert False

    except Exception as e:
        if str(e).endswith('The asset does not have enough physical storage.'):
            assert True
        else:
            assert False


def test_add_physical_to_no_existing_asset():
    try:
        manager.add_physical('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_add_virtual_to_active_asset():
    assert manager.add_virtual('token1', Item(10)) is None


def test_add_virtual_to_inactive_asset():
    try:
        manager.add_virtual('token', Item(10))
        assert False

    except Exception as e:
        if str(e).endswith('The asset does not have enough physical storage.'):
            assert True
        else:
            assert False


def test_add_virtual_to_no_existing_asset():
    try:
        manager.add_virtual('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_add_asset_to_active_asset():
    assert manager.add('token1', Item(10)) is None


def test_add_asset_to_inactive_asset():
    assert manager.add('token', Item(10)) is None


def test_add_asset_to_no_existing_asset():
    try:
        manager.add('token2', Item(10))
        assert False

    except KeyError:
        assert True


def test_get_asset():
    active_asset = manager.get('token1')
    inactive_asset = manager.get('token')
    non_existent = manager.get('token2')
    assert active_asset.is_active
    assert not inactive_asset.is_active
    assert non_existent is None


def test_get_tokens():
    tokens = manager.get_tokens()
    assert len(tokens) == 1
    assert tokens[0] == 'token1'


def test_get_assets_info():
    assets_infos = manager.get_info()

    assert len(assets_infos) == 2
    assert not assets_infos[0].is_active
    assert assets_infos[1].is_active


def test_get_active_assets_info():
    assets_infos = manager.get_active_info()

    assert len(assets_infos) == 1
    assert assets_infos[0].is_active


def test_deliver_physical():
    assert manager.deliver_physical('token1', 'item')
    try:
        manager.deliver_physical('token1', 'item')
        assert False
    except Exception as e:
        if str(e).endswith('The asset has no physical items to deliver.'):
            assert True

        else:
            assert False


def test_deliver_virtual():
    assert manager.deliver_virtual('token1', 'item')
    try:
        manager.deliver_virtual('token1', 'item')
        assert False
    except Exception as e:
        if str(e).endswith('The social asset has no virtual items to deliver.'):
            assert True

        else:
            assert False


def test_edit_asset():
    manager.edit('token1', 'route', [(10, 10)])
    assert manager.get('token1').route


def test_update_asset_location():
    manager.update_location('token1')
    assert manager.get('token1').location == (10, 10)


def test_clear_asset_physical_storage():
    for i in range(5):
        manager.add_physical('token1', Item(1))

    manager.clear_physical_storage('token1')
    assert not manager.get('token1').physical_storage_vector


def test_clear_asset_virtual_storage():
    for i in range(5):
        manager.add_virtual('token1', Item(1))

    manager.clear_virtual_storage('token1')
    assert not manager.get('token1').virtual_storage_vector


def test_restart():
    manager.restart(config_json['map'], config_json['socialAssets'])
    assert len(manager.get_tokens()) == 2
    assert manager.get('token').is_active
    assert manager.get('token1').is_active


def test_generate_objects():
    objects = manager.generate_objects(config_json['map'], config_json['socialAssets'])

    for obj in objects:
        if getattr(obj, 'profession') != 'doctor' and getattr(obj, 'profession') != 'teacher' and getattr(obj, 'profession') != 'nurse':
            assert False

        if 80 > getattr(obj, 'size') > 100:
            assert False

        if getattr(obj, 'speed') != 11:
            assert False

    assert True


if __name__ == '__main__':
    test_connect_asset()
    test_disconnect_asset()
    test_add_physical_to_active_asset()
    test_add_physical_to_inactive_asset()
    test_add_physical_to_no_existing_asset()
    test_add_virtual_to_active_asset()
    test_add_virtual_to_inactive_asset()
    test_add_virtual_to_no_existing_asset()
    test_add_asset_to_active_asset()
    test_add_asset_to_inactive_asset()
    test_add_asset_to_no_existing_asset()
    test_get_asset()
    test_get_tokens()
    test_get_assets_info()
    test_get_active_assets_info()
    test_deliver_physical()
    test_deliver_virtual()
    test_edit_asset()
    test_update_asset_location()
    test_clear_asset_physical_storage()
    test_clear_asset_virtual_storage()