class Flood:

    # still missing location attribute

    def __init__(self, period, dimensions, list_of_nodes):
        """
        [Object that represents a flood.]

        :param period: The amount of steps that a flood instance
        takes at the simulation.
        :param dimensions: Representation of the shape, size,
        latitude, longitude and 'disabled' nodes of a certain flood instance.
        :param photos: All 'photography events' that were randomly generated over a
        certain flood instance.
        :param water_samples: All 'collectible water samples' that were randomly generated
        over a certain flood instance.
        """
        self.type = 'flood'
        self.active = False
        self.period = period
        self.dimensions = dimensions
        self.list_of_nodes = list_of_nodes

    def json(self):
        """Return a json like representation of the object"""
        copy = self.__dict__.copy()
        del copy['list_of_nodes']
        del copy['period']
        return copy
