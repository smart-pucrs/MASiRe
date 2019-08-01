import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.communication.controllers.manager import Manager

manager = Manager()


def test_add():
    assert manager.add('token1_agent', {'name': 'Tester'}, 'agent')
    assert len(manager.agents_manager.agents) == 1

    assert manager.add('token1_agent', 'id1', 'socket')
    assert len(manager.agents_sockets_manager.socket_clients) == 1

    assert manager.add('token1_asset', {'name': 'Tester'}, 'social_asset')
    assert len(manager.social_assets_manager.social_assets) == 1

    assert manager.add('token1_asset', 'id1', 'socket')
    assert len(manager.assets_sockets_manager.socket_clients) == 1

    assert not manager.add('none', {'none': 'None'}, 'none')
    assert len(manager.agents_manager.agents) == 1
    assert len(manager.agents_sockets_manager.socket_clients) == 1
    assert len(manager.social_assets_manager.social_assets) == 1
    assert len(manager.assets_sockets_manager.socket_clients) == 1


def test_get():
    assert manager.get('token1_agent', 'agent') is not None
    assert not manager.get('token1_agent', 'agent').worker

    assert manager.get('token1_asset', 'social_asset') is not None
    assert not manager.get('token1_asset', 'social_asset').worker

    assert manager.get('token1_agent', 'socket') is not None
    assert manager.get('token1_agent', 'socket') == 'id1'

    assert manager.get('token1_asset', 'socket') is not None
    assert manager.get('token1_asset', 'socket') == 'id1'


def test_get_all():
    assert len(manager.get_all('agent')) == 1
    assert manager.get_all('agent')[0].token == 'token1_agent'

    assert len(manager.get_all('social_asset')) == 1
    assert manager.get_all('social_asset')[0].token == 'token1_asset'

    assert len(manager.get_all('socket')) == 2

    assert manager.get_all('none') is None


def test_get_actions():
    assert not manager.get_actions('agent')
    manager.agents_manager.agents['token1_agent'].worker = True
    manager.agents_manager.agents['token1_agent'].action_name = 'pass'

    assert manager.get_actions('agent')
    assert manager.get_actions('agent')[0]['action'] == 'pass'

    assert not manager.get_actions('social_asset')
    manager.social_assets_manager.social_assets['token1_asset'].worker = True
    manager.social_assets_manager.social_assets['token1_asset'].action_name = 'pass'

    assert manager.get_actions('social_asset')
    assert manager.get_actions('social_asset')[0]['action'] == 'pass'

    assert manager.get_actions('none') is None


def test_get_workers():
    assert manager.get_workers('agent')
    assert manager.get_workers('agent')[0].token == 'token1_agent'

    assert manager.get_workers('social_asset')
    assert manager.get_workers('social_asset')[0].token == 'token1_asset'

    assert manager.get_workers('none') is None


def test_get_kind():
    assert manager.get_kind('token1_agent') == 'agent'
    assert manager.get_kind('token1_asset') == 'social_asset'
    assert manager.get_kind('none') is None


def test_edit():
    assert manager.edit('token1_agent', 'worker', False, 'agent')
    assert manager.edit('token1_asset', 'worker', False, 'social_asset')
    assert not manager.edit('token1_agent', 'worker', None, 'none')

    assert not manager.get('token1_agent', 'agent').worker
    assert not manager.get('token1_asset', 'social_asset').worker

    assert manager.edit('token1_agent', 'worker', True, 'agent')
    assert manager.edit('token1_asset', 'worker', True, 'social_asset')

    assert manager.get('token1_agent', 'agent').worker
    assert manager.get('token1_asset', 'social_asset').worker


def test_clear_workers():
    assert manager.get_workers('agent')
    assert manager.get_workers('social_asset')
    assert manager.clear_workers()
    assert not manager.get_workers('agent')
    assert not manager.get_workers('social_asset')


def test_remove():
    assert not manager.remove('token1_agent', 'none')
    assert manager.remove('token1_agent', 'agent')
    assert not manager.agents_manager.agents
    assert not manager.agents_sockets_manager.socket_clients

    assert manager.remove('token1_asset', 'social_asset')
    assert not manager.social_assets_manager.social_assets
    assert not manager.assets_sockets_manager.socket_clients


if __name__ == '__main__':
    test_add()
    test_get()
    test_get_all()
    test_get_actions()
    test_get_workers()
    test_edit()
    test_clear_workers()
    test_remove()
