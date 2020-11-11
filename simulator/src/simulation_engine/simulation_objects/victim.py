import json

class Victim:
    """Class that represents a victim inside the simulation."""

    def __init__(self, flood_id: int, identifier: int, size: int, lifetime: int, location: tuple, photo: bool, **kwargs):
        self.type: str = 'victim'
        self.active: bool = False
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.size: int = size
        self.location: tuple = location
        self.lifetime: int = lifetime
        self.in_photo: bool = photo

    def dict(self):
        victim = self.__dict__.copy()
        del victim['active']
        del victim['type']
        return victim

    def to_json(self):
        return json.dumps(self.dict())

    def __str__(self):
        return self.to_json()