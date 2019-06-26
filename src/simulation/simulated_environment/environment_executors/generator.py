import json
import os
import random
from datetime import datetime
from directory_path import dir as root
from simulation.simulated_environment.environment_variables.events.flood import Flood
from simulation.simulated_environment.environment_variables.events.photo import Photo
from simulation.simulated_environment.environment_variables.events.victim import Victim
from simulation.simulated_environment.environment_variables.events.water_sample import WaterSample
from simulation.simulated_environment.environment_variables.route import Route


class Generator:

    def __init__(self, config, seed):
        self.total_photos: int = 0
        self.total_water_samples: int = 0
        self.total_victims: int = 0
        self.total_floods: int = 0
        self.total_social_assets: int = 0
        self.config = config
        self.router = Route(config['map']['map'], config['map']['proximity'])
        self.victim_counter: int = 0
        random.seed(seed)

    def generate_events(self) -> list:
        time_of_date = f'{datetime.today().hour}h_{datetime.today().minute}m'
        day = str(datetime.today().strftime("%d"))
        month = str(datetime.today().strftime("%B"))
        year = str(datetime.today().strftime("%Y"))
        events_path = root / 'files' / self.config['map']['id'] / year / month / day
        os.makedirs(events_path, exist_ok=True)
        events_path = str(events_path / time_of_date) + '_events.txt'

        file = open(events_path, 'w+')

        steps_number: int = self.config['map']['steps']
        events = [0] * steps_number
        flood = self.generate_flood()
        events[0] = dict(flood=flood, victims=self.generate_victims(flood.list_of_nodes, False),
                         water_samples=self.generate_water_samples(flood.list_of_nodes),
                         photos=self.generate_photos(flood.list_of_nodes), social_assets=self.generate_social_assets())
        locations = []
        for node in flood.list_of_nodes:
            locations.append(self.router.get_node_coord(node))

        json_event = {'0': dict(flood=events[0]['flood'].json_file(locations),
                                victims=[victim.json_file() for victim in events[0]['victims']],
                                water_sample=[water_sample.json_file() for water_sample in events[0]['water_samples']],
                                photos=[photo.json_file() for photo in events[0]['photos']],
                                social_asset=[social_asset.json_file() for social_asset in
                                              events[0]['social_assets']])}

        file.write(json.dumps(json_event, indent=4))
        file.flush()

        i: int = 1
        flood_probability: int = self.config['generate']['floodProbability']
        while i < steps_number:
            json_event = {}
            event = dict(flood=None, victims=[], water_samples=[], photos=[], social_assets=[])
            if random.randint(0, 99) <= flood_probability:
                event['flood'] = self.generate_flood()
                locations = []

                for node in flood.list_of_nodes:
                    locations.append(self.router.get_node_coord(node))

                nodes: list = event['flood'].list_of_nodes
                event['victims']: list = self.generate_victims(nodes, False)
                event['water_samples']: list = self.generate_water_samples(nodes)
                event['photos']: list = self.generate_photos(nodes)
                event['social_assets']: list = self.generate_social_assets()

                json_event['flood'] = event['flood'].json_file(locations)
                json_event['victims'] = [victim.json_file() for victim in event['victims']]
                json_event['water_samples'] = [water_sample.json_file() for water_sample in event['water_samples']]
                json_event['photos'] = [photo.json_file() for photo in event['photos']]
                json_event['social_assets'] = [social_asset.json_file() for social_asset in event['social_assets']]

                self.total_floods += 1
            step = {str(i): json_event}
            file.write(json.dumps(step, indent=4))
            file.flush()
            events[i] = event
            i += 1

        file.close()

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

        dimensions['location']: list = list(self.router.align_coords(flood_lat, flood_lon))

        # generate the list of nodes that are in the flood
        if dimensions['shape'] == 'circle':
            list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['radius'])

        else:
            if dimensions['height'] < dimensions['length']:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['height'])
            else:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['length'])

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

        i: int = 0
        while i < size:
            photo_location: list = list(self.router.get_node_coord(random.choice(nodes)))

            photo_victims: list = []
            if random.randint(0, 100) <= victim_probability:
                photo_victims = self.generate_victims(nodes, True)

            photos[i] = Photo(photo_size, photo_victims, photo_location)
            i += 1
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

        i: int = 0
        while i < size:
            self.victim_counter += 1

            victim_size: int = random.randint(victim_min_size, victim_max_size)
            victim_lifetime: int = random.randint(victim_min_lifetime, victim_max_lifetime)
            temp = random.choice(nodes)
            victim_location: list = list(self.router.get_node_coord(temp))

            victims[i] = Victim(victim_size, victim_lifetime, victim_location, photo_call)
            i += 1
        return victims

    def generate_water_samples(self, nodes: list) -> list:
        size: int = random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        )
        water_samples: list = [0] * size

        self.total_water_samples += size
        water_sample_size: int = self.config['generate']['waterSample']['size']

        i: int = 0
        while i < size:
            water_sample_location: list = list(self.router.get_node_coord(random.choice(nodes)))
            water_samples[i] = WaterSample(water_sample_size, water_sample_location)
            i += 1
        return water_samples

    def generate_social_assets(self) -> list:
        # min_lat, max_lat, min_lon, max_lon = self.config['map']['minLat'], self.config['map']['maxLat'], \
        #                                      self.config['map']['minLon'], self.config['map']['maxLon']
        #
        # size: int = random.randint(
        #     self.config['generate']['socialAsset']['minAmount'],
        #     self.config['generate']['socialAsset']['maxAmount']
        # )
        #
        # social_assets: list = [0] * size
        #
        # self.total_social_assets += size
        #
        # asset_min_size: int = self.config['generate']['socialAsset']['minSize']
        # asset_max_size: int = self.config['generate']['socialAsset']['maxSize']
        # professions: list = self.config['generate']['socialAsset']['profession']
        #
        # i: int = 0
        # while i < size:
        #     asset_location = [random.uniform(min_lat, max_lat), random.uniform(min_lon, max_lon)]
        #
        #     social_size = random.randint(asset_min_size, asset_max_size)
        #     profession = random.choice(professions)
        #
        #     social_assets[i] = SocialAsset(social_size, asset_location, profession)
        #     i += 1
        return []  # social_assets

    def set_seed(self, seed):
        random.seed(seed)
