import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.communication.helpers.social_assets_manager import SocialAssetsManager

manager = SocialAssetsManager()


def test_add():
    manager.add_social_asset('token1', {'name': 'Tester'})

    assert len(manager.social_assets) == 1
    assert manager.social_assets['token1'] is not None


def test_get():
    assert manager.get_social_asset('token1') is not None
    assert manager.get_social_asset('token3') is None


def test_get_all():
    manager.add_social_asset('token2', {'name': 'Tester'})
    assert len(manager.get_social_assets()) == 2
    assert manager.get_social_assets()[0].token == 'token1'
    assert manager.get_social_assets()[1].token == 'token2'


def test_get_actions():
    assert not manager.get_actions()
    manager.social_assets['token1'].worker = True
    manager.social_assets['token1'].action_name = 'pass'
    actions = manager.get_actions()
    assert actions
    assert actions[0]['action'] == 'pass'


def test_get_workers():
    assert manager.get_workers()
    assert manager.get_workers()[0].token == 'token1'
    assert len(manager.get_workers()) == 1


def test_edit():
    manager.edit_social_asset('token1', 'worker', False)
    assert not manager.get_social_asset('token1').worker
    manager.edit_social_asset('token1', 'worker', True)
    assert manager.get_social_asset('token1').worker


def test_clear_workers():
    assert manager.get_workers()
    assert manager.clear_workers() is None
    assert not manager.get_workers()


def test_remove():
    assert len(manager.get_social_assets()) == 2
    assert manager.remove_social_asset('token1') is None
    assert len(manager.get_social_assets()) == 1


if __name__ == '__main__':
    test_add()
    test_get()
    test_get_all()
    test_get_actions()
    test_get_workers()
    test_edit_agent()
    test_clear_workers()
    test_remove()
