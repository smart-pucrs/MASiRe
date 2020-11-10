from simulation_engine.simulation_objects.flood import Flood
from simulation_engine.simulation_objects.photo import Photo
from simulation_engine.simulation_objects.victim import Victim
from simulation_engine.simulation_objects.water_sample import WaterSample

from simulation_engine.simulation_objects.social_asset_marker import SocialAssetMarker


# def format_flood(flood: Flood) -> dict:
#     identifier: int = flood.identifier
#     period: int = flood.period
#     keeped: bool = flood.keeped
#     dimensions: dict = flood.dimensions
#     list_of_nodes: list = flood.list_of_nodes

#     return {
#         'type': 'flood',
#         'identifier': identifier,
#         'period': period,
#         'keeped': keeped,
#         'dimensions': dimensions,    
#         'propagation2': {
#             'max': flood.max_propagation,
#             'perStep': flood.propagation_per_step,
#             'victimProbability': flood.victim_probability
#         }
#         # 'list_of_nodes': list_of_nodes
#     }


def format_victims(victims: list) -> list:
    json_victims = []
    for victim in victims:
        json_victims.append(format_victim(victim))

    return json_victims


def format_victim(victim: Victim) -> dict:
    flood_id: int = victim.flood_id
    identifier: int = victim.identifier
    size: int = victim.size
    lifetime: int = victim.lifetime
    location: tuple = victim.location
    photo: bool = victim.in_photo

    return {
        'type': 'victim',
        'flood_id': flood_id,
        'identifier': identifier,
        'size': size,
        'lifetime': lifetime,
        'location': location,
        'in_photo': photo
    }


def format_photos(photos: list) -> list:
    json_photos = []

    for photo in photos:
        json_photos.append(format_photo(photo))

    return json_photos


def format_photo(photo: Photo) -> dict:
    flood_id: int = photo.flood_id
    identifier: int = photo.identifier
    size: int = photo.size
    victims: list = format_victims(photo.victims)
    location: tuple = photo.location

    return {
        'type': 'photo',
        'flood_id': flood_id,
        'identifier': identifier,
        'size': size,
        'victims': victims,
        'location': location,
    }


def format_water_samples(samples: list) -> list:
    json_samples = []

    for sample in samples:
        json_samples.append(format_water_sample(sample))

    return json_samples


def format_water_sample(water_sample: WaterSample) -> dict:
    flood_id: int = water_sample.flood_id
    identifier: int = water_sample.identifier
    size: int = water_sample.size
    location: tuple = water_sample.location

    return {
        'type': 'water_sample',
        'flood_id': flood_id,
        'identifier': identifier,
        'size': size,
        'location': location
    }


def format_assets(assets: list) -> list:
    json_assets = []

    for asset in assets:
        json_assets.append(format_social_asset_marker(asset))

    return json_assets


def format_social_asset_marker(asset: SocialAssetMarker) -> dict:
    identifier: int = asset.identifier
    location: tuple = asset.location
    profession: str = asset.profession
    abilities: list = asset.abilities
    resources: list = asset.resources

    return {
        'identifier': identifier,
        'location': location,
        'profession': profession,
        'abilities': abilities,
        'resources': resources
    }
