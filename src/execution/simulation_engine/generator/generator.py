import random
from simulation_engine.simulation_objects.flood import Flood
from simulation_engine.simulation_objects.photo import Photo
from simulation_engine.simulation_objects.victim import Victim
from simulation_engine.simulation_objects.water_sample import WaterSample


class Generator:
    """Class that generate all the events step, by step or separated if needed."""

    def __init__(self, config, map):
        self.map_variables: dict = config['map']
        self.generate_variables: dict = config['generate']
        self.map = map
        self.flood_id: int = 0
        self.victim_id: int = 0
        self.photo_victim_id: int = 0
        self.photo_id: int = 0
        self.water_sample_id: int = 0
        random.seed(config['map']['randomSeed'])

    def generate_events(self) -> list:
        """Generate all the events based on probabilities.

        If the probability of a flood to occur is bigger than the drawn number, an event is created. Except the first
        step which will always have a flood.

        :return list: All the steps containing either a dictionary with the event or a dictionary with a None flood."""

        steps_number: int = self.map_variables['steps']
        events = [0] * steps_number

        flood = self.generate_flood()
        nodes: list = flood.list_of_nodes
        event: dict = {
            'flood': flood,
            'victims': self.generate_victims(nodes),
            'water_samples': self.generate_water_samples(nodes),
            'photos': self.generate_photos(nodes)
        }

        events[0] = event

        flood_probability: int = self.generate_variables['flood']['probability']
        i: int = 1
        while i < steps_number:
            event: dict = {'flood': None, 'victims': [], 'water_samples': [], 'photos': []}
            if random.randint(1, 100) <= flood_probability:
                event['flood'] = self.generate_flood()
                nodes: list = event['flood'].list_of_nodes
                event['victims']: list = self.generate_victims(nodes)
                event['water_samples']: list = self.generate_water_samples(nodes)
                event['photos']: list = self.generate_photos(nodes)

            events[i] = event
            i += 1

        return events

    def generate_flood(self) -> Flood:
        """Generate one flood.

        Note: The only shape available currently is the circle.

        :return Flood: Flood event with dimensions gotten from the configuration file."""

        dimensions: dict = {'shape': 'circle' if random.randint(0, 0) == 0 else 'rectangle'}

        if dimensions['shape'] == 'circle':
            dimensions['radius'] = (
                random.uniform(self.generate_variables['flood']['circle']['minRadius'],
                               self.generate_variables['flood']['circle']['maxRadius'])
            )

        else:
            dimensions['height'] = (
                random.randint(self.generate_variables['flood']['rectangle']['minHeight'],
                               self.generate_variables['flood']['rectangle']['maxHeight'])
            )

            dimensions['length'] = (
                random.randint(self.generate_variables['flood']['rectangle']['minLength'],
                               self.generate_variables['flood']['rectangle']['maxLength'])
            )

        flood_lat: float = random.uniform(self.map_variables['minLat'], self.map_variables['maxLat'])
        flood_lon: float = random.uniform(self.map_variables['minLon'], self.map_variables['maxLon'])

        dimensions['location']: tuple = self.map.align_coords(flood_lat, flood_lon)

        if dimensions['shape'] == 'circle':
            list_of_nodes: list = self.map.nodes_in_radius(dimensions['location'], dimensions['radius'])

        else:
            if dimensions['height'] < dimensions['length']:
                list_of_nodes: list = self.map.nodes_in_radius(dimensions['location'], dimensions['height'])
            else:
                list_of_nodes: list = self.map.nodes_in_radius(dimensions['location'], dimensions['length'])

        period: int = random.randint(self.generate_variables['flood']['minPeriod'],
                                     self.generate_variables['flood']['maxPeriod'])

        self.flood_id = self.flood_id + 1

        return Flood(self.flood_id, period, dimensions, list_of_nodes)

    def generate_photos(self, nodes: list) -> list:
        """Generate a list of photo events inside the flood location.

        Note: Each photo can have N victims.

        :return list: List with all the photos generated."""

        victim_probability: int = self.generate_variables['photo']['victimProbability']
        photo_min_size: int = self.generate_variables['photo']['minSize']
        photo_max_size: int = self.generate_variables['photo']['maxSize']

        amount: int = random.randint(self.generate_variables['photo']['minAmount'],
                                     self.generate_variables['photo']['maxAmount'])
        photos: list = [0] * amount
        i: int = 0
        while i < amount:
            photo_location: tuple = self.map.get_node_coord(random.choice(nodes))
            photo_size: int = random.randint(photo_min_size, photo_max_size)
            photo_victims: list = []
            if random.randint(0, 100) <= victim_probability:
                photo_victims = self.generate_photo_victims(photo_location)

            photos[i] = Photo(self.photo_id, photo_size, photo_victims, photo_location)
            self.photo_id = self.photo_id + 1
            i += 1

        return photos

    def generate_victims(self, nodes: list) -> list:
        """Generate a list of victims.

        :return list: List of all the victims generated"""

        victim_min_size: int = self.generate_variables['victim']['minSize']
        victim_max_size: int = self.generate_variables['victim']['maxSize']

        victim_min_lifetime: int = self.generate_variables['victim']['minLifetime']
        victim_max_lifetime: int = self.generate_variables['victim']['maxLifetime']

        amount: int = random.randint(self.generate_variables['victim']['minAmount'],
                                     self.generate_variables['victim']['maxAmount'])
        victims: list = [0] * amount
        i: int = 0
        while i < amount:
            victim_size: int = random.randint(victim_min_size, victim_max_size)
            victim_lifetime: int = random.randint(victim_min_lifetime, victim_max_lifetime)
            victim_location: tuple = self.map.get_node_coord(random.choice(nodes))

            victims[i] = Victim(self.victim_id, victim_size, victim_lifetime, victim_location, False)
            self.victim_id = self.victim_id + 1
            i += 1

        return victims

    def generate_photo_victims(self, location: tuple) -> list:
        """Generate list of victims for photos.

        Note: the victims will be generated on the same location as the photo.

        :return list: List with all the generated Victims."""

        victim_min_size: int = self.generate_variables['victim']['minSize']
        victim_max_size: int = self.generate_variables['victim']['maxSize']

        victim_min_lifetime: int = self.generate_variables['victim']['minLifetime']
        victim_max_lifetime: int = self.generate_variables['victim']['maxLifetime']

        amount: int = random.randint(self.generate_variables['victim']['minAmount'],
                                     self.generate_variables['victim']['maxAmount'])
        victims: list = [0] * amount
        i: int = 0
        while i < amount:
            victim_size: int = random.randint(victim_min_size, victim_max_size)
            victim_lifetime: int = random.randint(victim_min_lifetime, victim_max_lifetime)

            victims[i] = Victim(self.victim_id, victim_size, victim_lifetime, location, True)
            self.victim_id = self.victim_id + 1
            i += 1

        return victims

    def generate_water_samples(self, nodes: list) -> list:
        """Generate list of water samples.

        :return list: List with all the generated water samples."""

        water_sample_min_size: int = self.generate_variables['waterSample']['minSize']
        water_sample_max_size: int = self.generate_variables['waterSample']['maxSize']

        amount: int = random.randint(self.generate_variables['waterSample']['minAmount'],
                                     self.generate_variables['waterSample']['maxAmount'])
        water_samples: list = [0] * amount
        i: int = 0
        while i < amount:
            water_sample_location: tuple = self.map.get_node_coord(random.choice(nodes))
            water_sample_size: int = random.randint(water_sample_min_size, water_sample_max_size)
            water_samples[i] = WaterSample(self.water_sample_id, water_sample_size, water_sample_location)
            self.water_sample_id = self.water_sample_id + 1
            i += 1

        return water_samples
