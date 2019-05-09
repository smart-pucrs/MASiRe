# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random
from simulation.simulated_enviroment.environment_variables.events.flood import Flood
from simulation.simulated_enviroment.environment_variables.events.photo import Photo
from simulation.simulated_enviroment.environment_variables.events.victim import Victim
from simulation.simulated_enviroment.environment_variables.events.social_asset import SocialAsset
from simulation.simulated_enviroment.environment_variables.events.water_sample import WaterSample
from simulation.simulated_enviroment.environment_variables.route import Route


class Generator:

    def __init__(self, config):
        self.total_photos: int = 0
        self.total_water_samples: int = 0
        self.total_victims: int = 0
        self.total_floods: int = 0
        self.total_social_assets: int = 0
        self.config = config
        self.router = Route(config['map']['map'])
        self.victim_counter: int = 0
        random.seed(config['map']['randomSeed'])

    def generate_events(self) -> list:
        events: list = [dict()] * self.config['map']['steps']
        events[0]['flood'] = self.generate_flood()

        for step in range(1, self.config['map']['steps']):
            if random.randint(0, 99) <= self.config['generate']['floodProbability']:
                events[step]['flood'] = self.generate_flood()
                nodes: list = events[step]['flood'].list_of_nodes
                events[step]['victims']: list = self.generate_victims(nodes, False)
                events[step]['water_samples']: list = self.generate_water_samples(nodes)
                events[step]['photos']: list = self.generate_photos(nodes)
                events[step]['social_assets']: list = self.generate_social_assets()

                self.total_floods += 1

        self.router.generate_routing_tables([obj['flood'] for obj in events])
        return events

    def generate_flood(self) -> Flood:
        # flood period
        period: int = random.randint(self.config['generate']['flood']['minPeriod'],
                                     self.config['generate']['flood']['maxPeriod'])

        # flood dimensions
        dimensions: dict = {'shape': 'circle'}

        # dimensions['shape'] = 'circle' if random.randint(0, 1) == 0 else 'rectangle'

        if dimensions['shape'] == 'circle':
            dimensions['radius'] = (
                random.uniform(self.config['generate']['flood']['circle']['minRadius'],
                               self.config['generate']['flood']['circle']['maxRadius'])
            )

        else:
            dimensions['height'] = (
                random.randint(self.config['generate']['flood']['rectangle']['minHeight'],
                               self.config['generate']['flood']['rectangle']['maxHeight'])
            )

            dimensions['length'] = (
                random.randint(self.config['generate']['flood']['rectangle']['minLength'],
                               self.config['generate']['flood']['rectangle']['maxLength'])
            )

        flood_lat: float = random.uniform(self.config['map']['minLat'], self.config['map']['maxLat'])
        flood_lon: float = random.uniform(self.config['map']['minLon'], self.config['map']['maxLon'])

        dimensions['coord']: list = list(self.router.align_coords(flood_lat, flood_lon))

        # generate the list of nodes that are in the flood
        if dimensions['shape'] == 'circle':
            list_of_nodes: list = self.router.nodes_in_radius(dimensions['coord'], dimensions['radius'])

        else:
            if dimensions['height'] < dimensions['length']:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['coord'], dimensions['height'])
            else:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['coord'], dimensions['length'])

        return Flood(period, dimensions, list_of_nodes)

    def generate_photos(self, nodes: list) -> list:
        size: int = random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        )
        photos: list = [0] * size

        self.total_photos += size

        victim_probability: int = self.config['generate']['photo']['victimProbability']
        photo_size: int = self.config['generate']['photo']['size']

        for i in range(size):
            photo_location: list = list(self.router.get_node_coord(random.choice(nodes)))

            photo_victims: list = []
            if random.randint(0, 100) <= victim_probability:
                photo_victims = self.generate_victims(nodes, True)

            photos[i] = Photo(photo_size, photo_victims, photo_location)

        return photos

    def generate_victims(self, nodes: list, photo_call: bool) -> list:
        size: int = random.randint(
            self.config['generate']['victim']['minAmount'],
            self.config['generate']['victim']['maxAmount']
        )
        victims: list = [0] * size

        self.total_victims += size

        victim_min_size: int = self.config['generate']['victim']['minSize']
        victim_max_size: int = self.config['generate']['victim']['maxSize']

        victim_min_lifetime: int = self.config['generate']['victim']['minLifetime']
        victim_max_lifetime: int = self.config['generate']['victim']['maxLifetime']

        for i in range(size):
            self.victim_counter += 1

            victim_size: int = random.randint(victim_min_size, victim_max_size)
            victim_lifetime: int = random.randint(victim_min_lifetime, victim_max_lifetime)
            victim_location: list = list(self.router.get_node_coord(random.choice(nodes)))

            victims[i] = Victim(victim_size, victim_lifetime, victim_location, photo_call)

        return victims

    def generate_water_samples(self, nodes: list) -> list:
        size: int = random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        )
        water_samples: list = [0] * size

        self.total_water_samples += size
        water_sample_size: int = self.config['generate']['waterSample']['size']

        for i in range(size):
            water_sample_location: list = list(self.router.get_node_coord(random.choice(nodes)))
            water_samples[i] = WaterSample(water_sample_size, water_sample_location)

        return water_samples

    def generate_social_assets(self) -> list:
        min_lat, max_lat, min_lon, max_lon = self.config['map']['minLat'], self.config['map']['maxLat'], \
                                             self.config['map']['minLon'], self.config['map']['maxLon']

        size: int = random.randint(
            self.config['generate']['socialAsset']['minAmount'],
            self.config['generate']['socialAsset']['maxAmount']
        )

        social_assets: list = [0] * size

        self.total_social_assets += size

        asset_min_size: int = self.config['generate']['socialAsset']['minSize']
        asset_max_size: int = self.config['generate']['socialAsset']['maxSize']
        professions: list = self.config['generate']['socialAsset']['profession']

        for i in range(size):
            asset_location: int = self.router.get_closest_node(random.uniform(min_lat, max_lat),
                                                               random.uniform(min_lon, max_lon))

            social_size = random.randint(asset_min_size, asset_max_size)
            profession = random.choice(professions)

            social_assets[i] = SocialAsset(social_size, asset_location, profession)

        return social_assets
