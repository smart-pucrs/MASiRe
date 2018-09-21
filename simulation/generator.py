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

      random_flood = random.randint(0, 100)
      random_photo = random.randint(0, 100)

      if random_flood <= self.config[generate][floodProbability] * 100: event_list[0] = generateFlood()
      if random_photo <= self.config[generate][photoProbability] * 100: event_list[1] = generatePhoto()

      events[step] = event_list

    return events

  def generateFlood(self):

    random_period = random.randint(self.config[generate][flood])

