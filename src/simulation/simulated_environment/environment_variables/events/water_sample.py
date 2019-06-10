class WaterSample:

    def __init__(self, size: int, location: list):
        """
        [Object <Consumable> that represents a water sample
        collected at a flood instance.]

        :param size: Amount of physical space that a water sample instance
        costs over the physical storage of an agent.
        :param node: Representation of the location where a water sample
        instance was collected.
        """

        self.type: str = 'water_sample'
        self.size: int = size
        self.location: list = location
        self.active: bool = False

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy

    def json_file(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        return copy
