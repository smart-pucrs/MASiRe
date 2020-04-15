class WaterSample:
    """Class that represents a water sample inside the simulation."""

    def __init__(self, flood_id: int, identifier: int, size: int, location: tuple, **kwargs):
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: tuple = location
