class SocialAssetMarker:
    def __init__(self, flood_id: int, identifier: int, location: tuple, profession: str, abilities: list, resources: list):
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.location: tuple = location
        self.profession: str = profession
        self.abilities: list = abilities
        self.resources: list = resources
        self.active: bool = True

    def __repr__(self):
        return str(self.__dict__)
