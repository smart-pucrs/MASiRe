class Victim:

    def __init__(self, size, lifetime, location, photo):
        """
             [Object <Consumable> that represents a victim instance revealed
             by a photography instance analysis.]

             :param size: Amount of physical space that a victim instance
             costs over the physical storage of an agent.
             :param lifetime: Number of steps that a victim instance must
             be delivered at the CDM.
             :param node: Representation of the location where the victim
             was found.
         """

        self.type = 'victim'
        self.size = size
        self.lifetime = lifetime
        self.active = False
        self.in_photo = photo
        self.location = location

    def __eq__(self, other):
        return self.size == other['size'] and self.location == other['location'] and self.lifetime == other['lifetime']

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['in_photo']
        return copy
