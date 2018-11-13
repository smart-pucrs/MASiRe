# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random
from src.simulation.data.events.flood import Flood
from src.simulation.data.events.photo import Photo
from src.simulation.data.events.victim import Victim
from src.simulation.data.events.water_sample import WaterSample
from pyroutelib3 import Router  # Import the router
from src.simulation.data.route import Route
import math

class Generator:

    def __init__(self, config):

        self.config = config
        #self.router = Router("car", config['map']['map'])  # Initialise router object from pyroutelib3
        self.router = Route(config['map']['map'])
        self.victim_counter = 0
        random.seed(config['map']['randomSeed'])

    def generate_events(self):
        events = [None for x in range(self.config['map']['steps'])]
        
        for step in range(len(events)):
            if step == 0: 
                events[step] = self.generate_flood()

            elif random.randint(0, 100) <= self.config['generate']['floodProbability']:
                events[step] = self.generate_flood()

        self.router.generate_routing_tables(events)
        return events, self.router

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
            list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('radius'))
            pass

        else:
            if dimensions.get('height')<dimensions.get('length'):
                list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('height'))
            else:
                list_of_nodes = self.router.nodes_in_radius(dimensions.get('coord'), dimensions.get('length'))

        photos = self.generate_photos(list_of_nodes)
        water_samples = self.generate_water_samples(list_of_nodes)

        return Flood(period, dimensions, photos, water_samples)

    def generate_photos(self, nodes):

        photos = [None for x in range(random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        ))]
        
        for x in range(len(photos)):

            photo_size = self.config['generate']['photo']['size']
            photo_location = random.choice(nodes)

            if random.randint(0, 100) <= self.config['generate']['photo']['victimProbability']:

                photo_victims = self.generate_victims(nodes)

            photos[x] = Photo(photo_size, photo_victims, photo_location)

        return photos

    def generate_victims(self, nodes):

        photo_victims = [None for x in range(random.randint(
                    self.config['generate']['victim']['minAmount'],
                    self.config['generate']['victim']['maxAmount']
        ))]

        for y in range(len(photo_victims)):
            
            self.victim_counter += 1

            victim_size = random.randint(
                self.config['generate']['victim']['minSize'],
                self.config['generate']['victim']['maxSize']
            )

            victim_lifetime = random.randint(
                self.config['generate']['victim']['minLifetime'],
                self.config['generate']['victim']['maxLifetime']
            )

            victim_location = random.choice(nodes)

            photo_victims[y] = Victim(self.victim_counter, victim_size, victim_lifetime, victim_location)

        return photo_victims

    def generate_water_samples(self, nodes):

        water_samples = [None for x in range(random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        ))]

        for x in range(len(water_samples)):

            water_sample_location = random.choice(nodes)

            water_samples[x] = WaterSample(self.config['generate']['waterSample']['size'], water_sample_location)

        return water_samples
