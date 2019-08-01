import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.communication.helpers.agents_manager import AgentsManager

manager = AgentsManager()


def test_add():
    manager.add_agent('token1', {'name': 'Tester'})

    assert len(manager.agents) == 1
    assert manager.agents['token1'] is not None


def test_get():
    assert manager.get_agent('token1') is not None
    assert manager.get_agent('token3') is None


def test_get_all():
    manager.add_agent('token2', {'name': 'Tester'})
    assert len(manager.get_agents()) == 2
    assert manager.get_agents()[0].token == 'token1'
    assert manager.get_agents()[1].token == 'token2'


def test_get_actions():
    assert not manager.get_actions()
    manager.agents['token1'].worker = True
    manager.agents['token1'].action_name = 'pass'
    actions = manager.get_actions()
    assert actions
    assert actions[0]['action'] == 'pass'


def test_get_workers():
    assert manager.get_workers()
    assert manager.get_workers()[0].token == 'token1'
    assert len(manager.get_workers()) == 1


def test_edit():
    manager.edit_agent('token1', 'worker', False)
    assert not manager.get_agent('token1').worker
    manager.edit_agent('token1', 'worker', True)
    assert manager.get_agent('token1').worker


def test_clear_workers():
    assert manager.get_workers()
    assert manager.clear_workers() is None
    assert not manager.get_workers()


def test_remove():
    assert len(manager.get_agents()) == 2
    assert manager.remove_agent('token1') is None
    assert len(manager.get_agents()) == 1


if __name__ == '__main__':
    test_add()
    test_get()
    test_get_all()
    test_get_actions()
    test_get_workers()
    test_edit_agent()
    test_clear_workers()
    test_remove()
