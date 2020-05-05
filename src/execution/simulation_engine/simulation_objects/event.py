import json
from abc import ABCMeta, abstractmethod
from .victim import Victim

class Event(object):
    __metaclass__ = ABCMeta

    def __init__(self, id:int, step:int, end: int, dimension: dict, propagation: dict,  **kwargs):
        self.active: bool = False
        self.type: str = 'flood'
        self.id = id
        self.step = step
        self.end: int = end
        self.dimension: dict = dimension
        self.nodes: list = []

        if propagation is not None:
            self.propagation = Propagation(propagation['max'], propagation['perStep'])
        else:
            self.propagation = Propagation(0,0)

        self.keeped = False
    
    def update_state(self, current_step):
        self.__active = self.expires <= current_step

        if (self.propagates):
            self.list_of_nodes.extend(propagates(self))
    
    def activate(self):
        self.__active = True
    def deactivate(self):
        self.__active = False
    def is_activated(self):
        return self.__active
    
    def affect_map(self, map, generator):
        self.nodes = generator.get_nodes(self.dimension['location'], self.dimension['shape'],self.dimension['radius'],map)
        self.propagation.affect_map(self.dimension,self.nodes,map,generator)
        return self.propagation

    def update_state(self):
        if len(self.propagation.nodesPerStep) > 0:
            self.nodes.extend(self.propagation.propagate())
            self.dimension['radius'] = self.dimension['radius'] * ((self.propagation.perStep/100)+1)

    @abstractmethod
    def propagate(self, map) -> list:
        raise NotImplementedError("Must override propagation")

    def __lt__(self, other):
        return self.step <= other.step

    def dict(self):
        event = self.__dict__.copy()
        del event['active']
        del event['keeped']
        del event['nodes']
        return event

    def to_json(self):
        return json.dumps(self.dict(),default=lambda o: o.__dict__)

    def __str__(self):
        return self.to_json()


class Propagation():
    def __init__(self, max, per_step):
        self.max = max
        self.perStep = per_step
        self.nodesPerStep = []
    
    def affect_map(self, dimension, nodes, map, generator):
        self.nodesPerStep = generator.generate_propagation(dimension['location'], dimension['radius'], self.max, self.perStep, nodes, map) 

    def propagate(self):
        return self.nodesPerStep.pop(0)

    def dict(self):
        prop = self.__dict__.copy()
        del prop['nodesPerStep']
        return prop

    def to_json(self):
        return json.dumps(self.dict())

    def __str__(self):
        return self.to_json()   