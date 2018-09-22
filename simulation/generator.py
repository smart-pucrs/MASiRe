# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/util/Generator.java

import random

from data.events.flood import Flood
from data.events.photo import Photo

class Generator:

  def __init__(self, config):

    self.config = config
    random.seed(config[randomSeed])

  def generateEvents(self):

    events = [None for x in range(self.config[steps])]

    for step in range(self.config[steps]):

      # generate floods (index 0) and photo events (index 1)

      event_list = [None, None]

      if random.randint(0, 100) <= self.config[generate][floodProbability] * 100: event_list[0] = generateFlood()

      events[step] = event_list

    return events

  def generateFlood(self):

    # flood period

    period = random.randint(self.config[generate][flood][minPeriod],
                            self.config[generate][flood][maxPeriod])

    # flood dimensions

    dimensions = dict()

    dimensions[shape] = 'circle' if random.randint(0, 100) % 2 == 0 else 'rectangle'

    if dimensions[shape] == 'circle':

      dimensions[radius] = (
        random.randint(self.config[generate][flood][circle][minRadius],
        self.config[generate][flood][circle][maxRadius])
      )
                              
    else:

      dimensions[height] = (
        random.randint(self.config[generate][flood][rectangle][minHeight],
        self.config[generate][flood][rectangle][maxHeight])
      )

      dimensions[lenght] = (
        random.randint(self.config[generate][flood][rectangle][minLenght],
        self.config[generate][flood][rectangle][maxLenght])
      )

    # flood photo events

    photo_events = [None for x in range(random.randint(
      self.config[generate][photo][minAmount],
      self.config[generate][photo][maxAmount]
    ))]

    for x in len(photo_events):
      
      photo_size = self.config[generate][photo][size]

      if random.randint()

      photo_events[x] = Photo()

    return Flood(random_period, )

