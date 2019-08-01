import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.communication.helpers.sockets_manager import SocketsManager

manager = SocketsManager()


def test_add():
    manager.add_socket('token1', 'id1')

    assert len(manager.socket_clients) == 1
    assert manager.socket_clients['token1'] is not None


def test_get():
    assert manager.get_socket('token1') is not None
    assert manager.get_socket('token3') is None


def test_get_all():
    manager.add_socket('token2', 'id2')
    assert len(manager.get_sockets()) == 2
    assert manager.get_sockets()[0] == 'id1'
    assert manager.get_sockets()[1] == 'id2'


def test_get_tokens():
    assert manager.get_tokens()
    assert manager.get_tokens()[0] == 'token1'
    assert len(manager.get_tokens()) == 2


def test_remove():
    assert len(manager.get_sockets()) == 2
    assert manager.remove_socket('token1') is None
    assert len(manager.get_sockets()) == 1


if __name__ == '__main__':
    test_add()
    test_get()
    test_get_all()
    test_get_tokens()
    test_remove()
