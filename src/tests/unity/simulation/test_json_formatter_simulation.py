import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))


from src.execution.simulation_engine.json_formatter import JsonFormatter


config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
formatter = JsonFormatter(config_path)


class Item:
    def __init__(self, type):
        self.type = type
        self.token = 'Mock'
        self.identifier = 0
        self.location = [10, 10]
        self.profession = type
        self.victims = []
        self.size = 10
        self.lifetime = 10
        self.social_assets = []
        self.physical_storage_vector = []
        self.physical_storage = 10
        self.physical_capacity = 10
        self.is_active = True
        self.carried = False
        self.location = [10, 10]
        self.last_action = None
        self.last_action_result = False
        self.role = type
        self.abilities = []
        self.resources = []
        self.max_charge = 10
        self.actual_battery = 10
        self.speed = 10
        self.route = []
        self.destination_distance = 0
        self.physical_capacity = 10
        self.physical_storage = 10
        self.physical_storage_vector = []
        self.virtual_capacity = 10
        self.virtual_storage = 10
        self.virtual_storage_vector = []
        self.social_assets = []


def test_restart():
    resp = formatter.restart()
    assert resp['status']


def test_log():
    log = formatter.log()
    assert log['status']
    assert log['message'] == 'New match generated.'

    log = formatter.log()
    assert not log['status']
    assert log['message'] == 'No more maps available for matches.'


def test_connect_agent():
    resp = formatter.connect_agent('token1_agent')
    assert resp['status']
    assert resp['message'] == 'Agent connected.'


def test_connect_social_asset():
    resp = formatter.connect_social_asset('token1_asset')
    assert resp['status']
    assert resp['message'] == 'Social asset connected.'


def test_disconnect_agent():
    resp = formatter.disconnect_agent('token1_agent')
    assert resp['status']
    assert resp['message'] == 'Agent disconnected.'


def test_disconnect_asset():
    resp = formatter.disconnect_social_asset('token1_asset')
    assert resp['status']
    assert resp['message'] == 'Social asset disconnected.'


def test_do_step():
    actions_tokens_list = [
        {'token': 'token2_agent', 'action': 'carry', 'parameters': ['token2_asset']},
        {'token': 'token2_asset', 'action': 'getCarried', 'parameters': ['token2_agent']},
        {'token': 'token3_agent', 'action': 'pass', 'parameters': []},
        {'token': 'token3_asset', 'action': 'rescueVictim', 'parameters': []}
    ]
    formatter.connect_agent('token2_agent')
    formatter.connect_social_asset('token2_asset')
    formatter.connect_agent('token3_agent')
    formatter.connect_social_asset('token3_asset')

    resp = formatter.do_step(actions_tokens_list)
    assert resp['status']
    assert resp['message'] == 'Step completed.'

    formatter.copycat.simulation.terminated = True
    resp = formatter.do_step(actions_tokens_list)
    assert resp['status']
    assert resp['message'] == 'Simulation finished.'
    assert not resp['actors']
    assert not resp['event']


def test_jsonify_agent():
    agent = formatter.copycat.simulation.cycler.agents_manager.get_active_info()[0]

    agent_formatted = formatter.jsonify_agent(agent)
    assert agent_formatted['token'] == agent.token
    assert agent_formatted['role'] == agent.role
    assert agent_formatted['size'] == agent.size
    assert agent_formatted['last_action'] == agent.last_action
    assert agent_formatted['last_action_result'] == agent.last_action_result
    assert agent_formatted['abilities'] == agent.abilities
    assert agent_formatted['resources'] == agent.resources
    assert agent_formatted['active']


def test_jsonify_agents():
    agents = list(formatter.copycat.simulation.cycler.agents_manager.get_active_info())

    agents_formatted = formatter.jsonify_agents(agents)

    for i in range(len(agents)):
        assert agents_formatted[i]['token'] == agents[i].token
        assert agents_formatted[i]['role'] == agents[i].role
        assert agents_formatted[i]['size'] == agents[i].size
        assert agents_formatted[i]['last_action'] == agents[i].last_action
        assert agents_formatted[i]['last_action_result'] == agents[i].last_action_result
        assert agents_formatted[i]['abilities'] == agents[i].abilities
        assert agents_formatted[i]['resources'] == agents[i].resources
        assert agents_formatted[i]['active']


def test_jsonify_asset():
    asset = formatter.copycat.simulation.cycler.social_assets_manager.get_active_info()[0]

    asset_formatted = formatter.jsonify_asset(asset)
    assert asset_formatted['token'] == asset.token
    assert asset_formatted['profession'] == asset.profession
    assert asset_formatted['size'] == asset.size
    assert asset_formatted['last_action'] == asset.last_action
    assert asset_formatted['last_action_result'] == asset.last_action_result
    assert asset_formatted['abilities'] == asset.abilities
    assert asset_formatted['resources'] == asset.resources
    assert asset_formatted['active']


def test_jsonify_assets():
    assets = formatter.copycat.simulation.cycler.social_assets_manager.get_active_info()

    assets_formatted = formatter.jsonify_assets(assets)
    for i in range(len(assets)):
        assert assets_formatted[i]['token'] == assets[i].token
        assert assets_formatted[i]['profession'] == assets[i].profession
        assert assets_formatted[i]['size'] == assets[i].size
        assert assets_formatted[i]['last_action'] == assets[i].last_action
        assert assets_formatted[i]['last_action_result'] == assets[i].last_action_result
        assert assets_formatted[i]['abilities'] == assets[i].abilities
        assert assets_formatted[i]['resources'] == assets[i].resources
        assert assets_formatted[i]['active']


def test_jsonify_events():
    event = formatter.copycat.simulation.cycler.steps[0]

    event_formatted = formatter.jsonify_events(event)
    assert event_formatted['flood']
    assert event_formatted['victims']
    assert event_formatted['photos']
    assert event_formatted['water_samples']

    event_formatted = formatter.jsonify_events({'flood':None})
    assert not event_formatted['flood']
    assert not event_formatted['victims']
    assert not event_formatted['photos']
    assert not event_formatted['water_samples']


def test_jsonify_delivered_items():
    victims_items = [Item('victim'), Item('victim')]
    photos_items = [Item('photo'), Item('photo'), Item('photo')]
    water_samples_items = [Item('water_sample'), Item('water_sample')]
    agents_items = [Item('agent'), Item('agent')]
    assets_items = [Item('social_asset'), Item('social_asset')]
    unknown_items = [Item('unknown'), Item('unknown')]
    mixed_items = [*victims_items, *photos_items, *water_samples_items, *agents_items, *assets_items, *unknown_items]

    try:
        assert formatter.jsonify_delivered_items(victims_items)
        assert formatter.jsonify_delivered_items(photos_items)
        assert formatter.jsonify_delivered_items(water_samples_items)
        assert formatter.jsonify_delivered_items(agents_items)
        assert formatter.jsonify_delivered_items(assets_items)
        assert formatter.jsonify_delivered_items(unknown_items)
        assert formatter.jsonify_delivered_items(mixed_items)

    except Exception:
        assert False


def test_jsonify_action_token_by_step():
    action_token_by_step = [(1, [('pass', 'token1')]), (2, [('pass', 'token2')])]

    result = formatter.jsonify_action_token_by_step(action_token_by_step)

    assert result[0]
    assert result[0]['step'] == 1
    assert result[0]['token_action']
    assert result[0]['token_action'][0]['token'] == 'token1'
    assert result[0]['token_action'][0]['action'] == 'pass'
    assert result[1]
    assert result[1]['step'] == 2
    assert result[1]['token_action']
    assert result[1]['token_action'][0]['token'] == 'token2'
    assert result[1]['token_action'][0]['action'] == 'pass'


def test_jsonify_amount_of_actions_by_step():
    amount_actions = [(1, 10), (2, 10), (3, 5)]

    result = formatter.jsonify_amount_of_actions_by_step(amount_actions)
    assert result[0]
    assert result[0]['step'] == 1
    assert result[0]['actions_amount'] == 10
    assert result[1]
    assert result[1]['step'] == 2
    assert result[1]['actions_amount'] == 10
    assert result[2]
    assert result[2]['step'] == 3
    assert result[2]['actions_amount'] == 5


def test_jsonify_actions_by_step():
    step_actions = [(1, ['pass', 'move']), (2, ['rescueVictim', 'deliverPhysical'])]

    result = formatter.jsonify_actions_by_step(step_actions)
    assert result[0]
    assert result[0]['step'] == 1
    assert result[0]['actions'] == ['pass', 'move']
    assert result[1]
    assert result[1]['step'] == 2
    assert result[1]['actions'] == ['rescueVictim', 'deliverPhysical']


if __name__ == '__main__':
    test_restart()
    test_log()
    test_connect_agent()
    test_connect_social_asset()
    test_disconnect_agent()
    test_disconnect_asset()
    test_do_step()
    test_jsonify_agent()
    test_jsonify_agents()
    test_jsonify_asset()
    test_jsonify_assets()
    test_jsonify_events()
    test_jsonify_delivered_items()
    test_jsonify_action_token_by_step()
    test_jsonify_amount_of_actions_by_step()
    test_jsonify_actions_by_step()