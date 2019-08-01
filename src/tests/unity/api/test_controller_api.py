import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import time
from src.execution.communication.controllers.controller import Controller


class RequestMock:
    def __init__(self, json=''):
        self.json = json
        self.sid = '10'

    def get_json(self, force):
        return self.json


controller = Controller(2, 2, 30, 'secret')


def test_check_secret():
    assert controller.check_secret('abc', 'abc')
    assert not controller.check_secret('abc', 'abd')
    assert not controller.check_secret('abc', 'ab')


def test_set_started():
    assert not controller.started
    controller.set_started()
    assert controller.started
    controller.set_started()
    assert not controller.started


def test_set_processing_actions():
    assert not controller.processing_actions
    controller.set_processing_actions()
    assert controller.processing_actions
    controller.set_processing_actions()
    assert not controller.processing_actions


def test_start_timer():
    assert controller.start_time is None
    controller.start_timer()
    assert controller.start_time is not None


def test_finish_connection_timer():
    controller.start_timer()
    start = time.time()

    assert not controller.start_time + 30 <= start
    controller.finish_connection_timer()
    assert controller.start_time + 30 <= start


def test_do_internal_verification():
    assert controller.do_internal_verification(RequestMock({'secret': 'secret'}))[0] == 1
    assert controller.do_internal_verification(RequestMock({'secret': 'wrong'}))[0] == 3
    assert controller.do_internal_verification(RequestMock({'non_secret_key': 'secret'}))[0] == 4


def test_do_agent_connection():
    controller.started = True
    controller.terminated = False
    controller.start_timer()
    assert controller.do_agent_connection(RequestMock('{: "wrong format" :}'))[0] == 2
    assert controller.do_agent_connection(RequestMock('"name"'))[0] == 4

    controller.finish_connection_timer()
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent"}'))[1] == 'Connection time ended.'

    controller.terminated = True
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent"}'))[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent"}'))[1] == 'Simulation has not started.'

    controller.started = True
    controller.terminated = False
    controller.start_timer()

    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent"}'))[0] == 1
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent"}'))[1] == 'Agent already connected.'
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent2"}'))[0] == 1
    assert controller.do_agent_connection(RequestMock('{"name": "TesterAgent3"}'))[1] == 'All possible agents already connected.'


def test_do_asset_connection():
    controller.started = True
    controller.terminated = False

    assert controller.do_social_asset_connection(RequestMock('{: "wrong format" :}'))[0] == 2
    assert controller.do_social_asset_connection(RequestMock('"name"'))[0] == 4

    controller.terminated = True
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset"}'))[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset"}'))[1] == 'Simulation has not started.'

    controller.started = True
    controller.terminated = False
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset"}'))[0] == 1
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset"}'))[1] == 'Social asset already connected.'
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset2"}'))[0] == 1
    assert controller.do_social_asset_connection(RequestMock('{"name": "TesterAsset3"}'))[1] == 'All possible social assets already connected.'


def test_do_agent_registration():
    controller.started = True
    controller.terminated = False
    controller.start_timer()
    token = list(controller.manager.agents_manager.agents.keys())[0]
    assert controller.do_agent_registration(RequestMock('{"token": "' + token + '"}'))[0] == 1

    assert controller.do_agent_registration(RequestMock('{"token": "' + token + '"}'))[1] == 'Agent already registered.'
    assert controller.do_agent_registration(RequestMock('{"token": "Unconnected"}'))[1] == 'Agent was not connected.'
    assert controller.do_agent_registration(RequestMock('{"non_token_key": ""}'))[1] == 'Object does not contain "token" as key.'
    assert controller.do_agent_registration(RequestMock('"non_dict"'))[1] == 'Object is not a dictionary.'

    assert controller.do_agent_registration(RequestMock('{: "wrong format" :}'))[0] == 2
    assert controller.do_agent_registration(RequestMock('"name"'))[0] == 4

    controller.finish_connection_timer()
    assert controller.do_agent_registration(RequestMock('{"name": "TesterAgent"}'))[1] == 'Connection time ended.'

    controller.terminated = True
    assert controller.do_agent_registration(RequestMock('{"name": "TesterAgent"}'))[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_agent_registration(RequestMock('{"name": "TesterAgent"}'))[1] == 'Simulation has not started.'


def test_do_asset_registration():
    controller.started = True
    controller.terminated = False
    token = list(controller.manager.social_assets_manager.social_assets.keys())[0]
    assert controller.do_social_asset_registration(RequestMock('{"token": "' + token + '"}'))[0] == 1

    assert controller.do_social_asset_registration(RequestMock('{"token": "' + token + '"}'))[1] == 'Social asset already registered.'
    assert controller.do_social_asset_registration(RequestMock('{"token": "Unconnected"}'))[1] == 'Social asset was not connected.'
    assert controller.do_social_asset_registration(RequestMock('{"non_token_key": ""}'))[1] == 'Object does not contain "token" as key.'
    assert controller.do_social_asset_registration(RequestMock('"non_dict"'))[1] == 'Object is not a dictionary.'

    assert controller.do_social_asset_registration(RequestMock('{: "wrong format" :}'))[0] == 2
    assert controller.do_social_asset_registration(RequestMock('"name"'))[0] == 4

    controller.terminated = True
    assert controller.do_social_asset_registration(RequestMock('{"name": "TesterAsset"}'))[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_social_asset_registration(RequestMock('{"name": "TesterAsset"}'))[1] == 'Simulation has not started.'
    
    
def test_do_agent_socket_connection():
    controller.started = True
    controller.terminated = False
    controller.start_timer()
    registered_token = list(controller.manager.agents_manager.agents.keys())[0]
    non_registered_token = list(controller.manager.agents_manager.agents.keys())[1]
    assert controller.do_agent_socket_connection(RequestMock(), '{"token": "' + registered_token + '"}')[0] == 1
    assert controller.do_agent_socket_connection(RequestMock(), '{"token": "' + registered_token + '"}')[1] == 'Socket already registered.'
    assert controller.do_agent_socket_connection(RequestMock(), '{"token": "' + non_registered_token + '"}')[1] == 'Agent was not registered.'
    assert controller.do_agent_socket_connection(RequestMock(), '{"token": "non_connected"}')[1] == 'Agent was not connected.'
    assert controller.do_agent_socket_connection(RequestMock(), '{"non_token_key": ""}')[1] == 'Object does not contain "token" as key.'
    assert controller.do_agent_socket_connection(RequestMock(), '"non_dict_obj"')[1] == 'Object is not a dictionary.'

    controller.finish_connection_timer()
    assert controller.do_agent_socket_connection(RequestMock(), '""')[1] == 'Connection time ended.'

    controller.terminated = True
    assert controller.do_agent_socket_connection(RequestMock(), '""')[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_agent_socket_connection(RequestMock(), '""')[1] == 'Simulation has not started.'


def test_do_asset_socket_connection():
    controller.started = True
    controller.terminated = False
    registered_token = list(controller.manager.social_assets_manager.social_assets.keys())[0]
    non_registered_token = list(controller.manager.social_assets_manager.social_assets.keys())[1]
    assert controller.do_social_asset_socket_connection(RequestMock(), '{"token": "' + registered_token + '"}')[0] == 1
    assert controller.do_social_asset_socket_connection(RequestMock(), '{"token": "' + registered_token + '"}')[1] == 'Socket already registered.'
    assert controller.do_social_asset_socket_connection(RequestMock(), '{"token": "' + non_registered_token + '"}')[1] == 'Social asset was not registered.'
    assert controller.do_social_asset_socket_connection(RequestMock(), '{"token": "non_connected"}')[1] == 'Social asset was not connected.'
    assert controller.do_social_asset_socket_connection(RequestMock(), '{"non_token_key": ""}')[1] == 'Object does not contain "token" as key.'
    assert controller.do_social_asset_socket_connection(RequestMock(), '"non_dict_obj"')[1] == 'Object is not a dictionary.'

    controller.terminated = True
    assert controller.do_social_asset_socket_connection(RequestMock(), '""')[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_social_asset_socket_connection(RequestMock(), '""')[1] == 'Simulation has not started.'


def test_do_agent_socket_disconnection():
    controller.started = True
    controller.terminated = False
    token = list(controller.manager.agents_sockets_manager.socket_clients.keys())[0]
    assert controller.do_agent_socket_disconnection('{"token": "' + token + '"}')[0] == 1
    assert controller.do_agent_socket_disconnection('{"token": "non_connected"}')[1] == 'Socket was not connected.'
    assert controller.do_agent_socket_disconnection('{"non_token_key": "token"}')[1] == 'Object does not contain "token" as key.'
    assert controller.do_agent_socket_disconnection('"non_dict_obj"')[1] == 'Object is not a dictionary.'

    controller.terminated = True
    assert controller.do_agent_socket_disconnection('""')[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_agent_socket_disconnection('""')[1] == 'Simulation has not started.'


def test_do_asset_socket_disconnection():
    controller.started = True
    controller.terminated = False
    token = list(controller.manager.assets_sockets_manager.socket_clients.keys())[0]
    assert controller.do_social_asset_socket_disconnection('{"token": "' + token + '"}')[0] == 1
    assert controller.do_social_asset_socket_disconnection('{"token": "non_connected"}')[1] == 'Socket was not connected.'
    assert controller.do_social_asset_socket_disconnection('{"non_token_key": "token"}')[1] == 'Object does not contain "token" as key.'
    assert controller.do_social_asset_socket_disconnection('"non_dict_obj"')[1] == 'Object is not a dictionary.'

    controller.terminated = True
    assert controller.do_social_asset_socket_disconnection('""')[1] == 'Simulation already terminated.'

    controller.started = False
    assert controller.do_social_asset_socket_disconnection('""')[1] == 'Simulation has not started.'


if __name__ == '__main__':
    test_set_started()
    test_set_processing_actions()
    test_start_timer()
    test_finish_connection_timer()
    test_do_internal_verification()
    test_do_agent_connection()
    test_do_asset_connection()
    test_do_agent_registration()
    test_do_asset_registration()
    test_do_agent_socket_connection()
    test_do_asset_socket_connection()
    test_do_agent_socket_disconnection()
    test_do_asset_socket_disconnection()
