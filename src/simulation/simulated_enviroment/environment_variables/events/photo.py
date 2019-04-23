class Photo:

    def __init__(self, size, victims, node):
        """
        [Object <Consumable> that represents a photography,
        resultant of a 'photograph' action over a flood instance.]

        :param size: Amount of virtual space that a photo instance
        costs over the virtual storage of an agent.
        :param victims: List of possible associated victims.
        :param node: Representation of the location where the photo
        instance was taken.
        """

        self.type = 'photo'
        self.size = size
        self.victims = victims
        self.node = node
        self.active = False

    def json(self):
        # victims = [victim.json() for victim in self.victims if victim.active]
        copy = self.__dict__.copy()
        del copy['victims']
        del copy['active']
        return copy

