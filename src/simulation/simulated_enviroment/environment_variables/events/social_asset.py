
class SocialAsset:
    def __init__(self, size, location, profession):
        """
             [Object <Consumable> that represents a social asset instance.]

             :param size: Amount of physical space that a social asset instance
             costs over the physical storage of an agent.
             :param node: Representation of the location where the social asset
             was found.
         """

        self.type = 'social_asset'
        self.size = size
        self.active = False
        self.location = location
        self.profession = profession

    def __eq__(self, other):
        self.location = other.location
        self.profession = other.profession
        self.size = other.size

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        return copy
