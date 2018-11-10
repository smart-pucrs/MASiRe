# based on https://github.com/agentcontest/massim/tree/master/server/src/main/java/massim/scenario/city/data/facilities


class Cdm:

    def __init__(self, location):
        """
        [Object that represents the simulation CDM,
        which will receive physical an virtual items from
        the active agents.]

        :param location: The location of the CDM at the simulation map.
        This variable will restrict the agent's actions in case of location inequality.
        """
        self.storedVolume = 0
        self.virtualItems = []
        self.physicalItems = []
        self.location = location  
