class Flood:

    # still missing location attribute

    def __init__(self, period: int, dimensions: dict, list_of_nodes: list):
        """
        [Object that represents a flood.]

        :param period: The amount of steps that a flood instance
        takes at the simulation.
        :param dimensions: Representation of the shape, size,
        latitude, longitude and 'disabled' nodes of a certain flood instance.
        :param list_of_nodes: A list with the nodes what the flood reaches
        """

        self.type: str = 'flood'
        self.active: bool = False
        self.period: int = period
        self.dimensions: dict = dimensions
        self.list_of_nodes: list = list_of_nodes

    def json(self):
        """Return a json like representation of the object"""
        copy = self.__dict__.copy()
        del copy['list_of_nodes']
        del copy['period']
        del copy['active']
        lat = copy['dimensions']['location'][0]
        lon = copy['dimensions']['location'][1]
        copy['dimensions']['location'] = {'lat': lat, 'lon': lon}
        return copy

    def json_file(self, locations):
        """Return a json like representation of the object to be write in a file"""
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        copy['list_of_nodes'] = locations
        return copy

