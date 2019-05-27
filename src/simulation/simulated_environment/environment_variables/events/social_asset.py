
class SocialAsset:
    def __init__(self, size: int, location: list, profession: str):
        """
             [Object <Consumable> that represents a social asset instance.]

             :param size: Amount of physical space that a social asset instance
             costs over the physical storage of an agent.
             :param node: Representation of the location where the social asset
             was found.
         """

        self.type: str = 'social_asset'
        self.size: int = size
        self.active: bool = False
        self.location: list = location
        self.profession: str = profession

    def __eq__(self, other):
        return self.location == other.location and self.size == other.size and self.profession == other.profession

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy
