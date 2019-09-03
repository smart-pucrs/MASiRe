class SocialAssetLayer:
    def __init__(self, identifier, location, profession):
        self.identifier = identifier
        self.location = location
        self.profession = profession
        self.active = False

    def __repr__(self):
        return str(self.__dict__)
