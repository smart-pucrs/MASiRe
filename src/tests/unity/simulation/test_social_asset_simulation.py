import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.simulation_engine.simulation_objects.social_asset import SocialAsset, FailedCapacity, FailedItemAmount


class Item:
    def __init__(self, size):
        self.type = 'item'
        self.size = size


def test_size():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)

    assert asset.size == 20


def test_add_physical_item():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))

    assert asset.physical_storage == 40
    assert len(asset.physical_storage_vector) == 1


def test_add_physical_item_capacity_error():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    try:
        asset.add_physical_item(Item(60))
        assert False

    except FailedCapacity:
        assert True


def test_add_virtual_item():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))

    assert asset.virtual_storage == 40
    assert len(asset.virtual_storage_vector) == 1


def test_add_virtual_item_capacity_error():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    try:
        asset.add_virtual_item(Item(60))
        assert False

    except FailedCapacity:
        assert True


def test_remove_physical_item_amount_equals_to_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))
    asset.remove_physical_item('item', 1)

    assert asset.physical_storage == 50
    assert len(asset.physical_storage_vector) == 0


def test_remove_physical_item_amount_equals_zero():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))

    asset.remove_physical_item('item', 0)

    assert asset.physical_storage == 40
    assert len(asset.physical_storage_vector) == 1


def test_remove_physical_item_amount_greater_than_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))

    asset.remove_physical_item('item', 3)

    assert asset.physical_storage == 50
    assert len(asset.physical_storage_vector) == 0


def test_remove_physical_item_amount_minor_than_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))
    asset.add_physical_item(Item(10))

    asset.remove_physical_item('item', 1)

    assert asset.physical_storage == 40
    assert len(asset.physical_storage_vector) == 1


def test_remove_physical_item_empty_vector():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)

    try:
        asset.remove_physical_item('item', 1)
        assert False

    except FailedItemAmount:
        assert True


def test_remove_virtual_item_amount_equals_to_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))
    asset.remove_virtual_item('item', 1)

    assert asset.virtual_storage == 50
    assert len(asset.virtual_storage_vector) == 0


def test_remove_virtual_item_amount_equals_zero():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))

    asset.remove_virtual_item('item', 0)

    assert asset.virtual_storage == 40
    assert len(asset.virtual_storage_vector) == 1


def test_remove_virtual_item_amount_greater_than_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))

    asset.remove_virtual_item('item', 3)

    assert asset.virtual_storage == 50
    assert len(asset.virtual_storage_vector) == 0


def test_remove_virtual_item_amount_minor_than_content():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))
    asset.add_virtual_item(Item(10))

    asset.remove_virtual_item('item', 1)

    assert asset.virtual_storage == 40
    assert len(asset.virtual_storage_vector) == 1


def test_remove_virtual_item_empty_vector():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)

    try:
        asset.remove_virtual_item('item', 1)
        assert False

    except FailedItemAmount:
        assert True


def test_clear_empty_physical_storage():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.clear_physical_storage()

    assert asset.physical_storage == 50
    assert len(asset.physical_storage_vector) == 0


def test_clear_non_empty_physical_storage():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_physical_item(Item(10))
    asset.clear_physical_storage()

    assert asset.physical_storage == 50
    assert len(asset.physical_storage_vector) == 0


def test_clear_empty_virtual_storage():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.clear_virtual_storage()

    assert asset.virtual_storage == 50
    assert len(asset.virtual_storage_vector) == 0


def test_clear_non_empty_virtual_storage():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    asset.add_virtual_item(Item(10))
    asset.clear_virtual_storage()

    assert asset.virtual_storage == 50
    assert len(asset.virtual_storage_vector) == 0


def test_disconnect():
    asset = SocialAsset('test_asset', [], [], (10, 10), 'doctor', 20, 10, 50, 50)
    
    asset.disconnect()

    assert not asset.is_active
    assert not asset.last_action_result
    assert asset.physical_storage == 0
    assert asset.virtual_storage == 0
    assert asset.destination_distance == 0
    assert len(asset.physical_storage_vector) == 0
    assert len(asset.virtual_storage_vector) == 0
    assert len(asset.social_assets) == 0


if __name__ == '__main__':
    test_size()
    test_add_physical_item()
    test_add_virtual_item()
    test_add_virtual_item_capacity_error()
    test_add_virtual_item_capacity_error()
    test_remove_physical_item_amount_equals_to_content()
    test_remove_physical_item_amount_equals_zero()
    test_remove_physical_item_amount_greater_than_content()
    test_remove_physical_item_amount_minor_than_content()
    test_remove_physical_item_empty_vector()
    test_remove_virtual_item_amount_equals_to_content()
    test_remove_virtual_item_amount_equals_zero()
    test_remove_virtual_item_amount_greater_than_content()
    test_remove_virtual_item_amount_minor_than_content()
    test_remove_virtual_item_empty_vector()
