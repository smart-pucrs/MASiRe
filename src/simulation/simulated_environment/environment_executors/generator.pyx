# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random
from simulation.simulated_environment.environment_variables.events.flood import Flood
from simulation.simulated_environment.environment_variables.events.photo import Photo
from simulation.simulated_environment.environment_variables.events.victim import Victim
from simulation.simulated_environment.environment_variables.events.social_asset import SocialAsset
from simulation.simulated_environment.environment_variables.events.water_sample import WaterSample
from simulation.simulated_environment.environment_variables.route import Route


class Generator:

    def __init__(self, dict config):
        cpdef int total_photos = 0;
        cpdef int total_water_samples = 0;
        cpdef int total_victims = 0;
        cpdef int total_floods = 0;
        cpdef int total_social_assets = 0;
        self.__dict__['total_photos'] = total_photos
        self.__dict__['total_water_samples'] = total_water_samples
        self.__dict__['total_victims'] = total_victims
        self.__dict__['total_floods'] = total_floods
        self.__dict__['total_social_assets'] = total_social_assets
        self.__dict__['config'] = config
        self.router = Route(config['map']['map'])
        random.seed(config['map']['randomSeed'])

    def generate_events(self) -> list:
        cdef list nodes;

        cdef list events = [dict()] * [self.config['map']['steps']][0];
        events.__getitem__(0)['flood'] = self.generate_flood()
        nodes = events.__getitem__(0)['flood'].list_of_nodes
        events.__getitem__(0)['victims'] = self.generate_victims(nodes, False)
        events.__getitem__(0)['water_samples'] = self.generate_water_samples(nodes)
        events.__getitem__(0)['photos'] = self.generate_photos(nodes)
        events.__getitem__(0)['social_assets'] = self.generate_social_assets()

        cdef int step = 1;
        cdef int max_steps = self.config['map']['steps'];
        cdef int flood_probability = self.config['generate']['floodProbability'];
        while step < max_steps:
            if random.randint(0, 99) <= flood_probability:
                events.__getitem__(step)['flood'] = self.generate_flood()
                nodes = events.__getitem__(step)['flood'].list_of_nodes
                events.__getitem__(step)['victims'] = self.generate_victims(nodes, False)
                events.__getitem__(step)['water_samples'] = self.generate_water_samples(nodes)
                events.__getitem__(step)['photos'] = self.generate_photos(nodes)
                events.__getitem__(step)['social_assets'] = self.generate_social_assets()

                self.total_floods += 1
            step += 1

        self.router.generate_routing_tables([obj['flood'] for obj in events])
        return events

    def generate_flood(self) -> Flood:
        # flood period
        cpdef int period = random.randint(self.config['generate']['flood']['minPeriod'],
                                          self.config['generate']['flood']['maxPeriod']);

        # flood dimensions
        cpdef dict dimensions = {'shape': 'circle'};

        # dimensions['shape'] = 'circle' if random.randint(0, 1) == 0 else 'rectangle'

        if dimensions.get('shape') == 'circle':
            dimensions.__setitem__('radius', random.uniform(self.config['generate']['flood']['circle']['minRadius'],
                                                            self.config['generate']['flood']['circle']['maxRadius']))

        else:
            dimensions.__setitem__('height', random.randint(self.config['generate']['flood']['rectangle']['minHeight'],
                                                            self.config['generate']['flood']['rectangle']['maxHeight']))

            dimensions.__setitem__('length', random.randint(self.config['generate']['flood']['rectangle']['minLength'],
                                                            self.config['generate']['flood']['rectangle']['maxLength']))

        cpdef float flood_lat = random.uniform(self.config['map']['minLat'], self.config['map']['maxLat']);
        cpdef float flood_lon = random.uniform(self.config['map']['minLon'], self.config['map']['maxLon']);

        dimensions.__setitem__('coord', list(self.router.align_coords(flood_lat, flood_lon)))

        # generate the list of nodes that are in the flood
        cpdef list list_of_nodes;
        if dimensions.get('shape') == 'circle':
            list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('radius'))

        else:
            if dimensions.get('height') < dimensions.get('length'):
                list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('height'))
            else:
                list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('length'))

        return Flood(period, dimensions, list_of_nodes)

    def generate_photos(self, nodes: list) -> list:
        cdef int size = random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        );
        cpdef list photos = [0] * size;

        self.total_photos += size

        cdef int victim_probability = self.config['generate']['photo']['victimProbability'];
        cpdef int photo_size = self.config['generate']['photo']['size'];


        cpdef list photo_location;
        cpdef list photo_victims;
        cdef int i = 0;

        while i < size:
            photo_location = list(self.router.get_node_coord(random.choice(nodes)))

            if random.randint(0, 100) <= victim_probability:
                photo_victims = self.generate_victims(nodes, True)

            photos.__setitem__(i, Photo(photo_size, photo_victims, photo_location))
            i += 1

        return photos

    def generate_victims(self, nodes: list, photo_call: bool) -> list:
        cdef int size = random.randint(
            self.config['generate']['victim']['minAmount'],
            self.config['generate']['victim']['maxAmount']
        );
        cpdef list victims = [0] * size

        self.total_victims += size

        cdef int victim_min_size = self.config['generate']['victim']['minSize']
        cdef int victim_max_size = self.config['generate']['victim']['maxSize']

        cdef int victim_min_lifetime = self.config['generate']['victim']['minLifetime']
        cdef int victim_max_lifetime = self.config['generate']['victim']['maxLifetime']

        cpdef int victim_size;
        cpdef int victim_lifetime;
        cpdef list victim_location;
        cdef int i = 0;

        while i < size:

            victim_size = random.randint(victim_min_size, victim_max_size)
            victim_lifetime = random.randint(victim_min_lifetime, victim_max_lifetime)
            victim_location = list(self.router.get_node_coord(random.choice(nodes)))

            victims.__setitem__(i, Victim(victim_size, victim_lifetime, victim_location, photo_call))
            i += 1

        return victims

    def generate_water_samples(self, nodes: list) -> list:
        cdef int size = random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        );

        cpdef list water_samples = [0] * size;

        self.total_water_samples += size
        cpdef int water_sample_size = self.config['generate']['waterSample']['size'];

        cdef int i = 0;
        cpdef list water_sample_location;
        while i < size:
            water_sample_location = list(self.router.get_node_coord(random.choice(nodes)))
            water_samples.__setitem__(i, WaterSample(water_sample_size, water_sample_location))
            i += 1

        return water_samples

    def generate_social_assets(self) -> list:
        cdef float min_lat = self.config['map']['minLat'];
        cdef float max_lat = self.config['map']['maxLat'];
        cdef float min_lon = self.config['map']['minLon'];
        cdef float max_lon = self.config['map']['maxLon']

        cdef int size = random.randint(
            self.config['generate']['socialAsset']['minAmount'],
            self.config['generate']['socialAsset']['maxAmount']
        );

        cpdef list social_assets = [0] * size;

        self.total_social_assets += size

        cdef int asset_min_size = self.config['generate']['socialAsset']['minSize'];
        cdef int asset_max_size = self.config['generate']['socialAsset']['maxSize'];
        cdef list professions = self.config['generate']['socialAsset']['profession'];

        cpdef long long asset_location;
        cpdef int social_size;
        cpdef str profession;
        cdef int i = 0;
        while i < size:
            asset_location = self.router.get_closest_node(random.uniform(min_lat, max_lat),
                                                                    random.uniform(min_lon, max_lon))

            social_size = random.randint(asset_min_size, asset_max_size)
            profession = random.choice(professions)

            social_assets.__setitem__(i, SocialAsset(social_size, asset_location, profession))
            i += 1

        return social_assets
