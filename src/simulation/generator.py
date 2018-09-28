# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util
# /Generator.java

import random

from .data.events.flood import Flood
from .data.events.photo import Photo
from .data.events.victim import Victim
from .data.events.water_sample import WaterSample


class Generator:

    def __init__(self, config):

        self.config = config
        random.seed(config['randomSeed'])

    def generateEvents(self):

        events = [None for x in range(self.config['steps'])]

        for step in range(len(events)):

            # generate floods (index 0) and photo events (index 1)

            if random.randint(0, 100) <= self.config['generate']['floodProbability'] * 10:
                events[step] = self.generateFlood()

        return events

    def generateFlood(self):

        # flood period

        period = random.randint(self.config['generate']['flood']['minPeriod'],
                                self.config['generate']['flood']['maxPeriod'])

        # flood dimensions

        dimensions = dict()

        dimensions['shape'] = 'circle' if random.randint(0, 100) % 2 == 0 else 'rectangle'

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

            dimensions['lenght'] = (
                random.randint(self.config['generate']['flood']['rectangle']['minLenght'],
                               self.config['generate']['flood']['rectangle']['maxLenght'])
            )

        # flood photo events

        photos = [None for x in range(random.randint(
            self.config['generate']['photo']['minAmount'],
            self.config['generate']['photo']['maxAmount']
        ))]

        for x in range(len(photos)):

            photo_size = self.config['generate']['photo']['size']

            if random.randint(0, 100) <= self.config['generate']['photo']['victimProbability'] * 100:

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

                    photo_victims[y] = Victim(victim_size, victim_lifetime)

            photos[x] = Photo(photo_size, photo_victims)

        # flood water sample events

        water_samples = [None for x in range(random.randint(
            self.config['generate']['waterSample']['minAmount'],
            self.config['generate']['waterSample']['maxAmount']
        ))]

        for x in range(len(water_samples)):
            water_samples[x] = WaterSample(self.config['generate']['waterSample']['size'])

        return Flood(period, dimensions, photos, water_samples)
