# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Role.java


class Role:
    def __init__(self, id, config):
        """
        [Sets the simulation role for an identified agent by the id tag.]

        :param id: The identifier that references a certain agent.
        :param config: The configuration file sent by the communication core
        to be manipulated.
        """
        self.id = id
        self.roads = config[id]['kind']
        self.speed = config[id]['speed']
        self.battery = config[id]['battery']
        self.percieve = config[id]['percieve']
        self.abilities = config[id]['abilities']
        self.virtual_capacity = config[id]['capacity_virtual']
        self.physical_capacity = config[id]['capacity_physical']
