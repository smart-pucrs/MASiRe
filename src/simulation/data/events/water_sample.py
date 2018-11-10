class WaterSample:

    def __init__(self, size, node):
        """
        [Object <Consumable> that represents a water sample
        collected at a flood instance.]

        :param size: Amount of physical space that a water sample instance
        costs over the physical storage of an agent.
        :param node: Representation of the location where a water sample
        instance was collected.
        """

        self.size = size
        self.node = node
        self.active = False