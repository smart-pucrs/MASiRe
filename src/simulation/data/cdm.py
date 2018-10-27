# based on https://github.com/agentcontest/massim/tree/master/server/src/main/java/massim/scenario/city/data/facilities


class Cdm:

    def __init__(self, location):
        self.storedVolume = 0
        self.virtualItems = []
        self.physicalItems = []
        self.location = location  

    def add_virtual(self, item, )
