class Flood:

    # still missing location attribute

    def __init__(self, period, dimensions, photos, water_samples, victims):
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

        self.period = period
        self.dimensions = dimensions
        self.photos = photos
        self.water_samples = water_samples
        self.active = False
        self.victims = victims

    def __str__(self):
        return 'FLOOD COMING'

    def __repr__(self):
        return 'FLOOD'
