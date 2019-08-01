import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.simulation_engine.simulation_objects.agent import Agent, FailedCapacity, FailedItemAmount


class Item:
    def __init__(self, size):
        self.type = 'item'
        self.size = size


def test_size():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    assert agent.size == 40


def test_discharge():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    agent.destination_distance = 10
    agent.discharge()

    assert agent.actual_battery == 18


def test_check_battery():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    assert agent.check_battery() == 18


def test_charge():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    agent.discharge()
    agent.charge()

    assert agent.actual_battery == 20


def test_add_physical_item():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))

    assert agent.physical_storage == 40
    assert len(agent.physical_storage_vector) == 1


def test_add_physical_item_capacity_error():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    try:
        agent.add_physical_item(Item(60))
        assert False

    except FailedCapacity:
        assert True


def test_add_virtual_item():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))

    assert agent.virtual_storage == 40
    assert len(agent.virtual_storage_vector) == 1


def test_add_virtual_item_capacity_error():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    try:
        agent.add_virtual_item(Item(60))
        assert False

    except FailedCapacity:
        assert True


def test_remove_physical_item_amount_equals_to_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))
    agent.remove_physical_item('item', 1)

    assert agent.physical_storage == 50
    assert len(agent.physical_storage_vector) == 0


def test_remove_physical_item_amount_equals_zero():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))

    agent.remove_physical_item('item', 0)

    assert agent.physical_storage == 40
    assert len(agent.physical_storage_vector) == 1


def test_remove_physical_item_amount_greater_than_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))

    agent.remove_physical_item('item', 3)

    assert agent.physical_storage == 50
    assert len(agent.physical_storage_vector) == 0


def test_remove_physical_item_amount_minor_than_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))
    agent.add_physical_item(Item(10))

    agent.remove_physical_item('item', 1)

    assert agent.physical_storage == 40
    assert len(agent.physical_storage_vector) == 1


def test_remove_physical_item_empty_vector():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    try:
        agent.remove_physical_item('item', 1)
        assert False

    except FailedItemAmount:
        assert True


def test_remove_virtual_item_amount_equals_to_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))
    agent.remove_virtual_item('item', 1)

    assert agent.virtual_storage == 50
    assert len(agent.virtual_storage_vector) == 0


def test_remove_virtual_item_amount_equals_zero():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))

    agent.remove_virtual_item('item', 0)

    assert agent.virtual_storage == 40
    assert len(agent.virtual_storage_vector) == 1


def test_remove_virtual_item_amount_greater_than_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))

    agent.remove_virtual_item('item', 3)

    assert agent.virtual_storage == 50
    assert len(agent.virtual_storage_vector) == 0


def test_remove_virtual_item_amount_minor_than_content():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))
    agent.add_virtual_item(Item(10))

    agent.remove_virtual_item('item', 1)

    assert agent.virtual_storage == 40
    assert len(agent.virtual_storage_vector) == 1


def test_remove_virtual_item_empty_vector():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)

    try:
        agent.remove_virtual_item('item', 1)
        assert False

    except FailedItemAmount:
        assert True


def test_clear_empty_physical_storage():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.clear_physical_storage()

    assert agent.physical_storage == 50
    assert len(agent.physical_storage_vector) == 0


def test_clear_non_empty_physical_storage():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_physical_item(Item(10))
    agent.clear_physical_storage()

    assert agent.physical_storage == 50
    assert len(agent.physical_storage_vector) == 0


def test_clear_empty_virtual_storage():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.clear_virtual_storage()

    assert agent.virtual_storage == 50
    assert len(agent.virtual_storage_vector) == 0


def test_clear_non_empty_virtual_storage():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.add_virtual_item(Item(10))
    agent.clear_virtual_storage()

    assert agent.virtual_storage == 50
    assert len(agent.virtual_storage_vector) == 0


def test_disconnect():
    agent = Agent('test_agent', (10, 10), [], [], 40, 'drone', 20, 10, 50, 50)
    agent.disconnect()

    assert not agent.is_active
    assert not agent.last_action_result
    assert agent.actual_battery == 0
    assert agent.physical_storage == 0
    assert agent.virtual_storage == 0
    assert agent.destination_distance == 0
    assert len(agent.physical_storage_vector) == 0
    assert len(agent.virtual_storage_vector) == 0
    assert len(agent.social_assets) == 0
