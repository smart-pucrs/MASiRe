from execution.simulation_engine.simulation_objects.event import Event 

class Flood(Event):

    def __init__(self, identifier: int, period: int, keeped: bool, dimensions: dict, list_of_nodes: list,
                 max_propagation: float, propagation_per_step: float, nodes_per_propagation: list):
        
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'flood'
        self.dimensions: dict = dimensions
        self.list_of_nodes: list = list_of_nodes
        self.period: int = period
        self.keeped: bool = keeped
        self.max_propagation =  (prop_info['maxPropagation'] / 100) * dimensions['radius'] + dimensions['radius']
        self.propagation_per_step = propagation_per_step
        self.nodes_per_propagation = nodes_per_propagation
      
    # def __init__(self, id, step, flood):
    #     super(Flood, self).__init__(id)
    #     self.type: str = 'flood'
    #     self.last_step: int = step + flood['period']
    #     self.initial_location = dimensions['location']

    #     self.dimensions: dict = dimensions
    #     self.list_of_nodes: list = list_of_nodes
        
    #     self.keeped: bool = flood['keeped']
    #     self.max_propagation = flood['dimensions']
    #     self.propagation_per_step = flood['list_of_nodes']
    #     self.nodes_per_propagation = nodes_per_propagation
    
    def __init__(self, *flood, **kwargs):
        super(Flood, self).__init__()
        for attr in flood:
            for key in attr:
                setattr(self, key, attr[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def update_state(self):
        if not self.keeped:
            self.period -= 1
            if not self.period:
                self.active = False

        if self.dimensions['radius'] < self.max_propagation:
            self.dimensions['radius'] = min(self.dimensions['radius'] + self.propagation_per_step, self.max_propagation)

        if self.nodes_per_propagation:
            self.list_of_nodes.extend(self.nodes_per_propagation.pop(0))

    def propagate(self, map):
        if (self.propagation_per_step == 0):
            return
        
        # prop_info = self.generate_variables['flood']['propagationInfo']
        # max_propagation = (prop_info['maxPropagation'] / 100) * dimensions['radius'] + dimensions['radius']
        # propagation_per_step = prop_info['propagationPerStep'] / 100 * dimensions['radius']

        # victim_probability: int = prop_info['victimsPerPropagationProbability']
        old_nodes: list = self.list_of_nodes

        # for prop in range(int(((prop_info['maxPropagation'] / 100) * dimensions['radius'] / propagation_per_step))):
        new_nodes = map.nodes_in_radius(self.dimensions['location'],
                                                self.dimensions['radius'] + self.propagation_per_step * prop)
        difference = self.get_difference(old_nodes, new_nodes)

        if random.randint(0, 100) < victim_probability:
            if difference:
                propagation.append(self.generate_victims_in_propagation(difference))
            else:
                propagation.append(self.generate_victims_in_propagation(new_nodes))

        nodes_propagation.append(difference)
        old_nodes = new_nodes