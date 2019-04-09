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
        self.virtual_items = {}
        self.physical_items = {}
        self.location = location  

    def add_physical_items(self, items, agent_id):
        if agent_id not in self.physical_items.keys():
            self.physical_items[agent_id] = []

        for item in items:
            self.physical_items[agent_id].append(item)

    def add_virtual_items(self, items, agent_id):
        if agent_id not in self.virtual_items.keys():
            self.virtual_items[agent_id] = []

        for item in items:
            self.virtual_items[agent_id].append(item)
