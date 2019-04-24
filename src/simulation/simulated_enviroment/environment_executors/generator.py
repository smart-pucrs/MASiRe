# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random
import math
from simulation.simulated_enviroment.environment_variables.events.flood import Flood
from simulation.simulated_enviroment.environment_variables.events.photo import Photo
from simulation.simulated_enviroment.environment_variables.events.victim import Victim
from simulation.simulated_enviroment.environment_variables.events.social_asset import SocialAsset
from simulation.simulated_enviroment.environment_variables.events.water_sample import WaterSample
from simulation.simulated_enviroment.environment_variables.route import Route


class Generator:

    def __init__(self, config):
        self.total_photos = 0
        self.total_water_samples = 0
        self.total_victims = 0
        self.total_floods = 0
        self.total_social_assets = 0
        self.config = config
        self.router = Route(config['map']['map'])
        self.victim_counter = 0
        random.seed(config['map']['randomSeed'])

    def generate_events(self):
        events = [None] * self.config['map']['steps']
        events[0] = self.generate_flood()

        for step in range(1, self.config['map']['steps'] + 1):
            if random.randint(0, 100) <= self.config['generate']['floodProbability'] * 10:
                events[step] = self.generate_flood()
                self.total_floods += 1

        self.router.generate_routing_tables(events)
        return events

    def generate_flood(self):
        # flood period
        period = random.randint(self.config['generate']['flood']['minPeriod'],
                                self.config['generate']['flood']['maxPeriod'])

        # flood dimensions
        dimensions = dict()

        dimensions['shape'] = 'circle'
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

        flood_lat = random.uniform(self.config['map']['minLat'], self.config['map']['maxLat'])
        flood_lon = random.uniform(self.config['map']['minLon'], self.config['map']['maxLon'])

        dimensions['coord'] = self.router.align_coords(flood_lat, flood_lon)

        # generate the list of nodes that are in the flood
        if dimensions['shape'] == 'circle':
            list_of_nodes = self.router.nodes_in_radius(dimensions['coord'], dimensions['radius'])

        else:
            if dimensions['height'] < dimensions['length']:
                list_of_nodes = self.router.nodes_in_radius(dimensions['coord'], dimensions['height'])
            else:
                list_of_nodes = self.router.nodes_in_radius(dimensions['coord'], dimensions['length'])

        photos = self.generate_photos(list_of_nodes)
        water_samples = self.generate_water_samples(list_of_nodes)
        victims = self.generate_victims(list_of_nodes, False)
        social_assets = self.generate_social_assets(list_of_nodes)

        return Flood(period, dimensions, photos, water_samples, victims, social_assets)

    def generate_photos(self, nodes):
        photos = [None] * random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        )

        self.total_photos += len(photos)

        for i in range(len(photos)):
            photo_size = self.config['generate']['photo']['size']
            photo_location = self.router.get_node_coord(random.choice(nodes))

            photo_victims = []
            if random.randint(0, 100) <= self.config['generate']['photo']['victimProbability']:
                photo_victims = self.generate_victims(nodes, True)

            photos[i] = Photo(photo_size, photo_victims, photo_location)

        return photos

    def generate_victims(self, nodes, photo_call):
        photo_victims = [None for _ in range(random.randint(
            self.config['generate']['victim']['minAmount'],
            self.config['generate']['victim']['maxAmount']
        ))]

        self.total_victims += len(photo_victims)

        for i in range(len(photo_victims)):
            self.victim_counter += 1

            victim_size = random.randint(
                self.config['generate']['victim']['minSize'],
                self.config['generate']['victim']['maxSize']
            )

            victim_lifetime = random.randint(
                self.config['generate']['victim']['minLifetime'],
                self.config['generate']['victim']['maxLifetime']
            )

            victim_location = self.router.get_node_coord(random.choice(nodes))

            photo_victims[i] = Victim(self.victim_counter, victim_size, victim_lifetime, victim_location, photo_call)

        return photo_victims

    def generate_water_samples(self, nodes):
        water_samples = [None for _ in range(random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        ))]

        self.total_water_samples += len(water_samples)

        for i in range(len(water_samples)):
            water_sample_location = self.router.get_node_coord(random.choice(nodes))
            water_samples[i] = WaterSample(self.config['generate']['waterSample']['size'], water_sample_location)

        return water_samples

    def generate_social_assets(self, nodes):
        social_assets = [None for _ in range(random.randint(
            self.config['generate']['socialAsset']['minAmount'],
            self.config['generate']['socialAsset']['maxAmount']
        ))]

        self.total_social_assets += len(social_assets)

        for i in range(len(social_assets)):
            asset_location = self.router.get_node_coord(random.choice(nodes))

            social_size = random.randint(
                self.config['generate']['socialAsset']['minSize'],
                self.config['generate']['socialAsset']['maxSize']
            )

            profession = random.choice(self.config['generate']['socialAsset']['profession'])
            social_assets[i] = SocialAsset(i, social_size, asset_location, profession)

        return social_assets

    def nodes_in_radius(self, coord, radius):
        # radius in kilometers
        result = []
        for node in self.router.rnodes:
            if self.router.distance(self.node_to_radian(node), self.coords_to_radian(coord)) <= radius:
                result.append(node)
        return result

    def node_to_radian(self, node):
        """Returns the radian coordinates of a given OSM node"""
        return self.coords_to_radian(self.router.nodeLatLon(node))

    def coords_to_radian(self, coords):
        """Maps a coordinate from degrees to radians"""
        return list(map(math.radians, coords))
