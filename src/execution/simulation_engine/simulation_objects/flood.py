class Flood:
    """Class that represents a flood inside the simulation."""

    def __init__(self, identifier: int, period: int, dimensions: dict, list_of_nodes: list):
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'flood'
        self.dimensions: dict = dimensions
        self.list_of_nodes: list = list_of_nodes
        self.period: int = period

