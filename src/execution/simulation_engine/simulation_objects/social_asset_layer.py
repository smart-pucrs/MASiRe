class SocialAssetLayer:
    def __init__(self, flood_id: int, identifier: int, location: tuple, profession: str):
        self.flood_id: int = flood_id
        self.identifier: int = identifier
        self.location: tuple = location
        self.profession: str = profession
        self.active: bool = False

    def __repr__(self):
        return str(self.__dict__)
