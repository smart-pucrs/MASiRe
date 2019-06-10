import json

from simulation.simulated_environment.environment_variables.events.flood import Flood
from simulation.simulated_environment.environment_variables.events.photo import Photo
from simulation.simulated_environment.environment_variables.events.social_asset import SocialAsset
from simulation.simulated_environment.environment_variables.events.victim import Victim
from simulation.simulated_environment.environment_variables.events.water_sample import WaterSample


def load_events(event_config_path):
    with open(event_config_path, 'r') as file:
        events = json.loads(file.read())

    sim_events = []
    for key in events:
        event_obj = dict(flood=None, victims=[], photos=[], water_samples=[], social_assets=[])
        if events[key]:
            event_obj['flood'] = get_flood(events[key]['flood'])
            event_obj['victims'] = [get_victim(victim) for victim in events[key]['victims']]
            event_obj['photos'] = [get_photo(photo) for photo in events[key]['photos']]
            event_obj['water_samples'] = [get_water_sample(water_sample) for water_sample in events[key]['water_samples']]
            event_obj['social_assets'] = [get_social_asset(social_asset) for social_asset in events[key]['social_assets']]
        sim_events.append(event_obj)
    return sim_events


def get_flood(json_obj):
    period = json_obj['period']
    dimensions = json_obj['dimensions']
    list_of_nodes = json_obj['list_of_nodes']
    flood = Flood(period, dimensions, list_of_nodes)
    flood.active = True

    return flood


def get_victim(json_obj):
    size = json_obj['size']
    lifetime = json_obj['lifetime']
    location = json_obj['location']
    photo = json_obj['in_photo']
    victim = Victim(size, lifetime, location, photo)
    victim.active = True

    return victim


def get_photo(json_obj):
    size = json_obj['size']
    victims = json_obj['victims']
    location = json_obj['location']
    photo = Photo(size, victims, location)
    photo.active = True

    return photo


def get_water_sample(json_obj):
    size = json_obj['size']
    location = json_obj['location']
    water_sample = WaterSample(size, location)
    water_sample.active = True

    return water_sample


def get_social_asset(json_obj):
    size = json_obj['size']
    location = json_obj['location']
    profession = json_obj['profession']
    social_asset = SocialAsset(size, location, profession)
    social_asset.active = True

    return social_asset
