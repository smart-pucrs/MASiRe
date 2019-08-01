class Photo:
    """Class that represents a photo event inside the simulation."""

    def __init__(self, identifier: int, size: int, victims: list, location: tuple):
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'photo'
        self.size: int = size
        self.location: tuple = location
        self.victims: list = victims
        self.analyzed: bool = False
