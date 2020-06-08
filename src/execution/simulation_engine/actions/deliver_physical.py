import types
from symbol import parameters

from ..exceptions.exceptions import (FailedCapacity, FailedItemAmount, FailedLocation, FailedNoMatch, FailedWrongParam)
from .action import Action


class DeliverPhysical(Action):
    action = ('deliverPhysical',[3])
    def __init__(self, agent, game_state, parameters):
        super(DeliverPhysical, self).__init__(agent, game_state, parameters, type='deliverPhysical',qtd_args=[1,2,3])
        self.mates = [("receivePhysical",1)]
        self.delivered_itens = game_state.delivered_items
        self.step = game_state.current_step

    def prepare(self):
        amount = 0 if self.parameters[2] < 0 else self.parameters[2]
        items = [item for item in self.agent.physical_storage_vector if item.type == self.parameters[1]]

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
        return (action.type == 'receivePhysical' and action.parameters[0] == self.agent.token)

    def execute(self, map, nodes, events, tasks):
        if len(self.parameters) == 3:
            removed_items = self.agent.remove_physical_item(self.parameters[1], self.mediator.shared_memory[1])
            self.mediator.notify(self, "removed_items", removed_items)
        else:
            if map.check_location(self.agent.location, self.cdm_location):
                if len(parameters) == 2:
                    delivered_items = self.agents_manager.remove_physical_item(self.parameters[0], 1) 
                else:
                    delivered_items = self.agents_manager.remove_physical_item(self.parameters[0], self.parameters[1]) 

                self.delivered_itens.append({'token': self.agent.token, 'kind': self.parameters[0], 'items': delivered_items,'step': self.step})
            else:
                raise FailedLocation('The agent is not located at the CDM.')
class DeliverFacility(Action):
    action = ('deliverPhysical',[1,2])
    def __init__(self, agent, game_state, parameters):
        super(DeliverFacility, self).__init__(agent, game_state, parameters, type='deliverPhysical',qtd_args=[1,2])
        self.step = game_state.current_step
        self.delivered_itens = game_state.delivered_items
        self.cdm_location = game_state.cdm_location

    def check_constraints(self, map):      
        itens = [item for item in self.agent.physical_storage_vector if item.type == self.parameters[0]]  
        if not itens:
            raise FailedItemAmount('The agent has no physical items of this kind to deliver.')

        if not map.check_location(self.agent.location, self.cdm_location):
            raise FailedLocation('The agent is not located at the CDM.')

    def execute(self, map, nodes, events, tasks):
        amount = 1 if len(self.parameters) != 2 else self.parameters[1]
        delivered_items = self.agent.remove_physical_item(self.parameters[0], self.parameters[1]) 

        self.delivered_itens.append({'token': self.agent.token, 'kind': self.parameters[0], 'items': delivered_items,'step': self.step})


class ReceivePhysical(Action):
    action = ('receivePhysical',[1])
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
            raise FailedCapacity(f'The receiving agent has {self.agent.physical_storage} of physical storage demand is {amount * itens[0].size}')

    def match(self, action):
        if (action.type == 'deliverPhysical' and action.parameters[0] == self.agent.token):
            if (self.parameters[0] == action.agent.token):
                return True
        return False

    def sync(self, sender, event, params):
        if event == 'removed_items':            
            for item in params:
                self.agent.add_physical_item(item)

    def execute(self, map, nodes, events, tasks):
        return {}