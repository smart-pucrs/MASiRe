import types
from symbol import parameters

from ..exceptions.exceptions import (FailedCapacity, FailedItemAmount,
                                     FailedNoMatch, FailedWrongParam)
from .action import Action


class DeliverVirtual(Action):
   
    def __init__(self, agent, skills, resources, parameters):
        super(DeliverVirtual, self).__init__(agent, skills, resources, parameters, type='deliverVirtual',min_args=1, max_args=3)
        self.mates = [("receiveVirtual",1)]

    def prepare(self):
        amount = max(0, self.parameters[2])
        items = [item for item in self.agent.virtual_storage_vector if item.type == self.parameters[0]]

        self.mediator.shared_memory.append(items)
        self.mediator.shared_memory.append(amount)

    def check_parameters(self):   
        if (len(self.parameters) != 1 and len(self.parameters) != 3):
            raise FailedWrongParam(f'wrong number of parameters, expecting 1 or 3 parameters')

    def check_constraints(self):        
        if not self.mediator.shared_memory[0]:
            raise FailedItemAmount('The agent has no virtual items of this kind to deliver.')
      
    def match(self, action):
        return (action.type == 'receiveVirtual' and action.parameters[1] == self.agent.token)

    def execute(self, map, nodes, events):
        if len(self.parameters) == 3:
            self._transmit_to_agent()
        else:
            self._transmit_to_facility()

    def _transmit_to_facility(self):
        return {}
    def _transmit_to_agent(self):
        amount = self.mediator.shared_memory[1]
        items = self.agent.remove_virtual_item(self.parameters[0], amount)

        self.mediator.notify(self, "removed_items", items)

class ReceiveVirtual(Action):
   
    def __init__(self, agent, skills, resources, parameters):
        super(ReceiveVirtual, self).__init__(agent, skills, resources, parameters, type='receiveVirtual',min_args=1, max_args=1)
        self.mates = [("deliverVirtual",1)]

    def prepare(self):
        pass

    def check_parameters(self):        
        pass

    def check_constraints(self):
        itens = self.mediator.shared_memory[0]
        amount = self.mediator.shared_memory[1]
        if self.agent.virtual_storage < amount * itens[0].size:
            raise FailedCapacity('The receiving agent does not have enough virtual storage.')

    def match(self, action):
        if (action.type == 'deliverVirtual' and action.parameters[1] == self.agent.token):
            if (self.parameters[0] == action.agent.token):
                return True
        return False

    def sync(self, sender, event, params):
        if event == 'removed_items':            
            for item in params:
                self.agent.add_virtual_item(item)

    def execute(self, map, nodes, events):
        return {}