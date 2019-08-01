class WaterSample:
    """Class that represents a water sample inside the simulation."""

    def __init__(self, identifier: int, size: int, location: tuple):
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: tuple = location
