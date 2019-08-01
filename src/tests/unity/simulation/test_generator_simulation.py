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
g = Generator(config_json, simulation_map)
nodes = None


def test_generate_events():
    global nodes
    events = g.generate_events()
    nodes = events[0]['flood'].list_of_nodes
    assert len(events) == 10
    assert events[0]['flood'] is not None


def test_generate_flood():
    flood = g.generate_flood()
    assert not flood.active
    assert 40 <= flood.period <= 80


def test_generate_victims():
    victims = g.generate_victims(nodes)
    assert 20 <= len(victims) <= 40


def test_generate_photos():
    photos = g.generate_photos(nodes)
    assert 20 <= len(photos) <= 40


def test_generate_water_samples():
    water_samples = g.generate_water_samples(nodes)
    assert 20 <= len(water_samples) <= 40


if __name__ == '__main__':
    test_generate_events()
    test_generate_flood()
    test_generate_victims()
    test_generate_photos()
    test_generate_water_samples()
