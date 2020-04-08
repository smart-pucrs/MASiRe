import json

class Victim:
    """Class that represents a victim inside the simulation."""

    def __init__(self, flood_id: int, identifier: int, size: int, lifetime: int, location: tuple, photo: bool):
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'victim'
        self.size: int = size
        self.location: tuple = location
        self.lifetime: int = lifetime
        self.in_photo: bool = photo

    def to_json(self):
        return json.dumps(self.__dict__)