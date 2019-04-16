class Victim:

    def __init__(self, id, size, lifetime, node):
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

        self.id = id
        self.type = 'victim'
        self.size = size
        self.lifetime = lifetime
        self.active = False
        self.node = node

    def json(self):
        return self.__dict__
