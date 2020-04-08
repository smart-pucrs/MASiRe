from abc import ABCMeta, abstractmethod

class Event(object):
    __metaclass__ = ABCMeta

    def __init__(self, id):
        self.__active = False
        self.__identifier = id
    def __init__(self):
        self.__active = False
    
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
    

    @abstractmethod
    def propagate(self, map) -> list:
        raise NotImplementedError("Must override propagation")

    
