
class SocialAsset:
    def __init__(self, id, size, node, profession):
        """
             [Object <Consumable> that represents a social asset instance.]

             :param size: Amount of physical space that a social asset instance
             costs over the physical storage of an agent.
             :param node: Representation of the location where the social asset
             was found.
         """

        self.id = id
        self.type = 'social_asset'
        self.size = size
        self.active = False
        self.node = node
        self.profession = profession

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        return copy
