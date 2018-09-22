# based on https://github.com/agentcontest/massim/tree/master/server/src/main/java/massim/scenario/city/data/facilities


class cdm:

    location = None
    storedVolume = 0
    virtualItems = 0
    physicalItems = 0

    def __init__(self, location=None):
        self.location = location #not implemented yet

    def charge(self, agent):
        agent.charge()

    def deliver(self, kind, total):
        if kind == 'virtual':
            self.setVirtualItems(total)
        elif kind == 'physical':
            self.setPhysicalItems(total)

    def setVirtualItems(self, total):
        self.virtualItems += total
        self.storedVolume += total

    def setPhysicalItems(self, total):
        self.physicalItems += total
        self.storedVolume += total
