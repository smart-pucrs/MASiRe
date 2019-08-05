"""Nesse arquivo de teste deve ser testado o module manager que está na pasta da API dentro de execution.
Deve ser testadas todos os métodos tentando passar por todas as linhas do código de cada função, ou seja,
testar todos os retornos e erros da função"""
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
token = 'token'
token_2 = 'token_2'
obj_info = {'name': 'Test'}


def test_add():

    assert manager.add(token, obj_info, 'agent')
    assert len(manager.agents_manager.agents) == 1

    assert manager.add(token_2, obj_info, 'social_asset')
    assert len(manager.social_assets_manager.social_assets) == 1

    assert manager.add(token, obj_info, 'socket')
    assert len(manager.agents_sockets_manager.socket_clients) == 1
    assert not len(manager.assets_sockets_manager.socket_clients)

    assert manager.add(token_2, obj_info, 'socket')
    assert len(manager.agents_manager.agents) == 1
    assert len(manager.assets_sockets_manager.socket_clients) == 1

    assert not manager.add(token, obj_info, 'None')

    assert len(manager.agents_manager.agents) == 1
    assert len(manager.social_assets_manager.social_assets) == 1
    assert len(manager.agents_sockets_manager.socket_clients) == 1
    assert len(manager.assets_sockets_manager.socket_clients) == 1


def test_get():
    assert manager.get(token, 'agent') is not None
    assert manager.get('None', 'agent') is None

    assert manager.get(token_2, 'social_asset') is not None
    assert manager.get('None', 'social_asset') is None

    assert manager.get(token, 'socket') is not None
    assert manager.get(token_2, 'socket') is not None
    assert manager.get('None', 'socket') is None

    assert manager.get(token, 'None') is None


def test_get_all():
    assert len(manager.get_all('agent')) == 1

    assert len(manager.get_all('social_asset')) == 1

    l1, l2 = manager.get_all('socket')
    assert len(l1) == 1 and len(l2) == 1

    assert manager.get_all('None') is None


def test_get_actions():
    assert not manager.get_actions('agent')

    manager.get(token, 'agent').worker = True
    manager.get(token, 'agent').action_name = 'pass'
    assert manager.get_actions('agent') == [{'action': 'pass', 'parameters': [], 'token': token}]

    manager.get(token_2, 'social_asset').worker = True
    manager.get(token_2, 'social_asset').action_name = 'pass'
    assert manager.get_actions('social_asset') == [{'action': 'pass', 'parameters': [], 'token': token_2}]

    assert manager.get_actions('None') is None


def test_workers():
    assert len(manager.get_workers('agent')) == 1

    assert len(manager.get_workers('social_asset')) == 1

    assert manager.get_workers('None') is None


def test_edit():
    assert manager.edit(token, 'registered', True, 'agent')
    assert manager.get(token, 'agent').registered

    assert manager.edit(token, 'worker', False, 'agent')
    assert not manager.get(token, 'agent').worker

    assert manager.edit(token, 'action_name', 'move', 'agent')
    assert manager.get(token, 'agent').action_name == 'move'

    assert manager.edit(token, 'action_params', [0, 1], 'agent')
    assert manager.get(token, 'agent').action_params == [0, 1]

    assert manager.edit(token, 'agent_info', {'name': 'new_name'}, 'agent')
    assert manager.get(token, 'agent').agent_info == {'name': 'new_name'}

    assert manager.edit(token_2, 'registered', True, 'social_asset')
    assert manager.get(token_2, 'social_asset').registered

    assert manager.edit(token_2, 'worker', False, 'social_asset')
    assert not manager.get(token_2, 'social_asset').worker

    assert manager.edit(token_2, 'action_name', 'move', 'social_asset')
    assert manager.get(token_2, 'social_asset').action_name == 'move'

    assert manager.edit(token_2, 'action_params', [0, 1], 'social_asset')
    assert manager.get(token_2, 'social_asset').action_params == [0, 1]

    assert manager.edit(token_2, 'agent_info', {'name': 'new_name'}, 'social_asset')
    assert manager.get(token_2, 'social_asset').agent_info == {'name': 'new_name'}


def test_clear_workers():
    assert manager.clear_workers()
    assert manager.get_workers('agent') == []
    assert manager.get_workers('social_asset') == []


def test_remove():
    assert manager.remove(token, 'agent')
    assert not len(manager.agents_manager.agents)
    assert not len(manager.agents_sockets_manager.socket_clients)

    assert manager.remove(token_2, 'social_asset')
    assert not len(manager.social_assets_manager.social_assets)
    assert not len(manager.assets_sockets_manager.socket_clients)

    assert not manager.remove(token, 'None')


if __name__ == '__main__':
    test_add()
    test_get()
    test_get_all()
    test_get_actions()
    test_edit()
    test_clear_workers()
    test_remove()