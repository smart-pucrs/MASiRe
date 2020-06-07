import sys
import pathlib
import pytest

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.map import Map
from src.execution.simulation_engine.generator.generator import Generator
from src.execution.simulation_engine.simulation_helpers.map import Map

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
simulation_map = Map(config_json['map']['maps'][0], config_json['map']['proximity'], config_json['map']['movementRestrictions'])
nodes = Generator(config_json, simulation_map).generate_events(simulation_map)[0]['flood'].nodes
node = None
@pytest.fixture
def cdm():
    return [-30.110815,-51.21199]
@pytest.fixture
def epicentre():
    return [-30.1093449, -51.2079282]
@pytest.fixture
def radius():
    return 0.0039
@pytest.fixture
def event(epicentre, radius):
    # e = Event(self, id:int, step:int, end: int, dimension: dict, propagation: dict,  **kwargs)
    e = {'location': epicentre, 'radius': radius}
    return e

def test_get_closest_node():
    global node
    location = [-30.1058249, -51.2120934]
    node = simulation_map.get_closest_node(*location)

    assert node is not None
    assert node == 1407603256

def test_get_node_coord():
    assert simulation_map.get_node_coord(node) == (-30.1058249, -51.2120934)

def test_check_proximity():
    assert simulation_map.check_proximity(10, 10.00004)
    assert not simulation_map.check_proximity(10, 10.0006)

def test_check_location():
    assert simulation_map.check_location([10, 10], [10.00004, 10.00004])
    assert not simulation_map.check_location([10, 10], [10.0006, 10.0006])

def test_nodes_in_radius(epicentre, radius):
    epicentre_node = simulation_map.router.findNode(*epicentre)
    epicentre_lat_lon = simulation_map.router.nodeLatLon(epicentre_node)
    assert epicentre_lat_lon[0] == epicentre[0]
    assert epicentre_lat_lon[1] == epicentre[1]
    nodes = simulation_map.nodes_in_radius(epicentre, radius)
    assert epicentre_node in nodes

def test_get_route():
    start_coord = -30.1058249, -51.2120934
    end_coord = -30.1072904, -51.2087442

    assert simulation_map.get_route(start_coord, end_coord, 'car', 10, nodes, [])[1]
    assert simulation_map.get_route(start_coord, end_coord, 'drone', 10, nodes, [])[1]

    assert simulation_map.get_route((-30.1098256, -51.2115133), (-30.110234, -51.2119344), 'boat', 10, nodes, [])[1]

def test_ground_out_to_in(cdm, epicentre, radius, event):
    nodes = simulation_map.nodes_in_radius(epicentre, radius)
    result, route, dist = simulation_map.get_route(cdm, epicentre, 'car', 7, nodes, [event])
    assert route != []
    last_node = route[-1]
    assert last_node[2] == True
    assert last_node[0] == epicentre[0]
    assert last_node[1] == epicentre[1]

def test_ground_in_to_out(cdm, epicentre, radius, event):
    nodes = simulation_map.nodes_in_radius(epicentre, radius)
    result, route, dist = simulation_map.get_route(epicentre, cdm, 'car', 7, nodes, [event])
    assert route != []
    last_node = route[-1]
    assert last_node[2] == False
    assert last_node[0] == cdm[0]
    assert last_node[1] == cdm[1]

def test_ground_in_to_in(epicentre, radius, event):
    nodes = simulation_map.nodes_in_radius(epicentre, radius)
    loc = [epicentre[0]+0.001, epicentre[1]]
    result, route, dist = simulation_map.get_route(loc, epicentre, 'car', 7, nodes, [event])
    assert route != []
    for lat, lon, is_in in route:
        assert is_in   

def test_euclidean_distance():
    assert round(simulation_map.euclidean_distance([10, 20], [20, 30]), 2) == 14.14
