# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random

from src.simulation.data.events.flood import Flood
from src.simulation.data.events.photo import Photo
from src.simulation.data.events.victim import Victim
from src.simulation.data.events.water_sample import WaterSample


class Generator:

    def __init__(self, config):

        self.config = config
        random.seed(config['map']['randomSeed'])

    def generate_events(self):

        events = [None for x in range(self.config['map']['steps'])]

        for step in range(len(events)):

            # generate floods (index 0) and photo events (index 1)

            if random.randint(0, 100) <= self.config['generate']['floodProbability']:
                events[step] = self.generate_flood()

        return events

    def generate_flood(self):

        # flood period

        period = random.randint(self.config['generate']['flood']['minPeriod'],
                                self.config['generate']['flood']['maxPeriod'])

        # flood dimensions

        dimensions = dict()

        dimensions['shape'] = 'circle' if random.randint(0, 1) == 0 else 'rectangle'

        if dimensions['shape'] == 'circle':

            dimensions['radius'] = (
                random.randint(self.config['generate']['flood']['circle']['minRadius'],
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

        photos = self.generate_photos()
        water_samples = self.generate_water_samples()

        return Flood(period, dimensions, photos, water_samples)

    def generate_photos(self):

        photos = [None for x in range(random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        ))]

        for x in range(len(photos)):

            photo_size = self.config['generate']['photo']['size']

            if random.randint(0, 100) <= self.config['generate']['photo']['victimProbability'] * 100:

                photo_victims = self.generate_victims()

            photos[x] = Photo(photo_size, photo_victims)

        return photos

    def generate_victims(self):

        photo_victims = [None for x in range(random.randint(
                    self.config['generate']['victim']['minAmount'],
                    self.config['generate']['victim']['maxAmount']
        ))]

        for y in range(len(photo_victims)):
            
            victim_size = random.randint(
                self.config['generate']['victim']['minSize'],
                self.config['generate']['victim']['maxSize']
            )

            victim_lifetime = random.randint(
                self.config['generate']['victim']['minLifetime'],
                self.config['generate']['victim']['maxLifetime']
            )

            photo_victims[y] = Victim(victim_size, victim_lifetime, 0)

        return photo_victims

    def generate_water_samples(self):

        water_samples = [None for x in range(random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        ))]

        for x in range(len(water_samples)):
            water_samples[x] = WaterSample(self.config['generate']['waterSample']['size'],1)

        return water_samples
