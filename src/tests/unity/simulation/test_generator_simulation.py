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
from src.execution.simulation_engine.generator.loader import Loader
from src.execution.simulation_engine.simulation_helpers.cycle import Cycle


config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
simulation_map = Map(config_json['map']['maps'][0], config_json['map']['proximity'], config_json['map']['movementRestrictions'])
g = Generator(config_json, simulation_map)
nodes = None


# def test_generate_events():
#     global nodes
#     events = g.generate_events()
#     nodes = events[0]['flood'].list_of_nodes
#     assert len(events) == 10
#     assert events[0]['flood'] is not None

def test_generate_events():
    generator = Generator(config_json, simulation_map)
    events_1 = generator.generate_events(simulation_map)

    path = pathlib.Path(__file__).parents[4] / "src/tests/unity/test_events_same.txt"
    Loader.write_first_match(config_json,events_1, generator.generate_social_assets(), generator, path)

    loader = Loader(config_json, simulation_map, path)
    events_2 = loader.generate_events(simulation_map)  

    for i, e in enumerate(events_1):
        assert e['step'] == events_2[i]['step']
        if e['step'] >= 0:
            assert e['flood'].id == events_2[i]['flood'].id
            assert len(e['photos']) == len(events_2[i]['photos'])
            assert len(e['water_samples']) == len(events_2[i]['water_samples'])
            assert len(e['propagation']) == len(events_2[i]['propagation'])

def test_generate_social_assets():
    generator = Generator(config_json, simulation_map)
    generator.generate_events(simulation_map)
    social_assets_1 = generator.generate_social_assets()

    path = pathlib.Path(__file__).parents[4] / "src/tests/unity/test_events_file.txt"

    loader = Loader(config_json, simulation_map, path)
    social_assets_2 = loader.generate_social_assets() 

    for i, sa in enumerate(social_assets_1):
        assert len(sa.abilities) == len(social_assets_2[i].abilities)
        assert sa.location[0] == social_assets_2[i].location[0]
        assert sa.location[1] == social_assets_2[i].location[1]
        assert len(sa.resources) == len(social_assets_2[i].resources)

def test_generate_flood():
    flood, prop = g.generate_event(step=26)
    assert "flood" == flood.type
    assert not flood.active
    assert 26+40 <= flood.end <= 26+80


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
