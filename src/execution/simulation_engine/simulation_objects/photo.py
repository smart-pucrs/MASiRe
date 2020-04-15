# from execution.simulation_engine.simulation_objects.victim import Victim

class Photo:
    """Class that represents a photo event inside the simulation."""

    def __init__(self, flood_id: int, identifier: int, size: int, location: tuple, victims: list, **kwargs):
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'photo'
        self.size: int = size
        self.location: tuple = location
        self.victims: list = victims
        self.analyzed: bool = False
        