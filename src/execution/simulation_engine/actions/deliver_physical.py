import types
from symbol import parameters

from ..exceptions.exceptions import (FailedCapacity, FailedItemAmount, FailedLocation, FailedNoMatch, FailedWrongParam)
from .action import Action


class DeliverPhysical(Action):
    def __init__(self, agent, game_state, parameters):
        super(DeliverPhysical, self).__init__(agent, game_state, parameters, type='deliverPhysical',qtd_args=[1,2,3])
        self.mates = [("receivePhysical",1)]
        self.delivered_itens = game_state.delivered_items
        self.step = game_state.current_step

    def prepare(self):
        amount = 0 if self.parameters[2] < 0 else self.parameters[2]
        items = [item for item in self.agent.physical_storage_vector if item.type == self.parameters[0]]

        self.mediator.shared_memory.append(items)
        self.mediator.shared_memory.append(amount)

    def check_parameters(self):   
        pass

    def check_constraints(self, map):        
        if not self.mediator.shared_memory[0]:
            raise FailedItemAmount('The agent has no physical items of this kind to deliver.')

        if not self.mediator.agents_same_location(map):
            raise FailedLocation('agents in different locations.')
      
    def match(self, action):
        return (action.type == 'receivePhysical' and action.parameters[1] == self.agent.token)

    def execute(self, map, nodes, events, tasks):
        if len(self.parameters) == 3:
            removed_items = self.agent.remove_physical_item(self.parameters[0], self.mediator.shared_memory[1])
            self.mediator.notify(self, "removed_items", removed_items)
        else:
            if map.check_location(agent.location, self.cdm_location):
                if len(parameters) == 2:
                    delivered_items = self.agents_manager.remove_physical_item(self.parameters[0], 1) 
                else:
                    delivered_items = self.agents_manager.remove_physical_item(self.parameters[0], self.parameters[1]) 

                self.delivered_itens.append({'token': self.agent.token, 'kind': self.parameters[0], 'items': delivered_items,'step': self.step})
            else:
                raise FailedLocation('The agent is not located at the CDM.')


class ReceivePhysical(Action):
    def __init__(self, agent, game_state, parameters):
        super(ReceivePhysical, self).__init__(agent, game_state, parameters, type='receivePhysical',qtd_args=[1])
        self.mates = [("deliverPhysical",1)]

    def prepare(self):
        pass

    def check_parameters(self):        
        pass

    def check_constraints(self, map):
        itens = self.mediator.shared_memory[0]
        amount = self.mediator.shared_memory[1]
        if self.agent.physical_storage < amount * itens[0].size:
            raise FailedCapacity('The receiving agent does not have enough physical storage.')

    def match(self, action):
        if (action.type == 'deliverPhysical' and action.parameters[1] == self.agent.token):
            if (self.parameters[0] == action.agent.token):
                return True
        return False

    def sync(self, sender, event, params):
        if event == 'removed_items':            
            for item in params:
                self.agent.add_physical_item(item)

    def execute(self, map, nodes, events, tasks):
        return {}