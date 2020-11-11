class SocialAssetMarker:
    def __init__(self, identifier: int, location: tuple, profession: str, abilities: list, resources: list):
        self.identifier: int = identifier
        self.location: tuple = location
        self.profession: str = profession
        self.abilities: list = abilities
        self.resources: list = resources
        self.active: bool = True

    def __repr__(self):
        return str(self.__dict__)
