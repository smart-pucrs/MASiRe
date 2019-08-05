import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.map import Map
from src.execution.simulation_engine.generator.generator import Generator


config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
simulation_map = Map(config_json['map']['maps'][0], config_json['map']['proximity'])
nodes = Generator(config_json, simulation_map).generate_events()[0]['flood'].list_of_nodes
node = None


def test_get_closest_node():
    global node
    location = [-30.1058249, -51.2120934]
    node = simulation_map.get_closest_node(*location)

    assert node is not None
    assert node == 1407603256


def test_get_node_coord():
    assert simulation_map.get_node_coord(node) == (-30.1058249, -51.2120934)


def test_check_proximity():
    assert simulation_map.check_proximity(10, 10.004)
    assert not simulation_map.check_proximity(10, 10.006)


def test_check_location():
    assert simulation_map.check_location([10, 10], [10.004, 10.004])
    assert not simulation_map.check_location([10, 10], [10.006, 10.006])


def test_get_route():
    start_coord = -30.1058249, -51.2120934
    end_coord = -30.1072904, -51.2087442

    assert simulation_map.get_route(start_coord, end_coord, 'car', 10, nodes)[1]
    assert simulation_map.get_route(start_coord, end_coord, 'drone', 10, nodes)[1]

    assert simulation_map.get_route((-30.1098256, -51.2115133), (-30.110234, -51.2119344), 'boat', 10, nodes)[1]


def test_generate_route_for_drone():
    assert simulation_map.generate_coordinates_for_drones([10, 10], [30, 30], 10)[0]


def test_generate_route_for_boat():
    assert simulation_map.generate_coordinates_for_boats((-30.1098256, -51.2115133), (-30.110234, -51.2119344), 10, nodes)[0]
    assert not simulation_map.generate_coordinates_for_boats((-30.1135454, -51.2098736), (-30.110234, -51.2119344), 10, nodes)[0]


def test_decrease_until_reached():
    points = simulation_map.decrease_until_reached(11, 10, 500)
    assert len(points) == 4
    assert points[0] == 10.75

    points = simulation_map.decrease_until_reached(10, 11, 10)
    assert len(points) == 1
    assert points[0] == 11

    points = simulation_map.decrease_until_reached(10, 10, 10)
    assert len(points) == 1
    assert points[0] == 10


def test_increase_until_reached():
    points = simulation_map.increase_until_reached(10, 11, 500)
    assert len(points) == 4
    assert points[0] == 10.25

    points = simulation_map.increase_until_reached(11, 10, 10)
    assert len(points) == 1
    assert points[0] == 10

    points = simulation_map.increase_until_reached(10, 10, 10)
    assert len(points) == 1
    assert points[0] == 10


def test_euclidean_distance():
    assert round(simulation_map.euclidean_distance([10, 20], [20, 30]), 2) == 14.14


if __name__ == '__main__':
    test_get_closest_node()
    test_get_node_coord()
    test_check_location()
    test_get_route()
    test_generate_route_for_drone()
    test_generate_route_for_boat()
    test_decrease_until_reached()
    test_increase_until_reached()
    test_euclidean_distance()
