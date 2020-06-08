from .action import Action
from ..exceptions.exceptions import (FailedCapacity, FailedItemAmount, FailedLocation, FailedNoMatch, FailedWrongParam)

class CarryAgent(Action):
    action = ('carry',[1])
    def __init__(self, agent, game_state, parameters):
        super(CarryAgent, self).__init__(agent, game_state, parameters, type='carry',qtd_args=[1,2,3])
        self.mates = [("getCarried",1)]

    def check_constraints(self, map):        
        if not self.mediator.agents_same_location(map):
            raise FailedLocation('agents in different locations.')

        size = self.mediator.notify(self, 'ask_size', [])
        if (self.agent.physical_storage < size[0]):
            raise FailedCapacity('cannot carry agent')
      
    def match(self, action):
        return (action.type == 'getCarried' and action.parameters[0] == self.agent.token)

    def sync(self, sender, event, params):
        if event == 'ready':     
            self.agent.add_physical_item(sender.agent)

class GetCarried(Action):
    action = ('getCarried',[1])
    def __init__(self, agent, game_state, parameters):
        super(GetCarried, self).__init__(agent, game_state, parameters, type='getCarried',qtd_args=[1])
        self.mates = [("carry",1)]

    def match(self, action):
        if (action.type == 'carry' and action.parameters[0] == self.agent.token):
            if (self.parameters[0] == action.agent.token):
                return True
        return False

    def sync(self, sender, event, params):
        if event == 'ask_size':            
            return self.agent.size

    def execute(self, map, nodes, events, tasks):
        self.mediator.notify(self, 'ready', [])
        self.agent.carried = True

class DeliverAgent(Action):
    action = ('deliverAgent',[1])
    def __init__(self, agent, game_state, parameters):
        super(DeliverAgent, self).__init__(agent, game_state, parameters, type='deliverAgent',qtd_args=[1,2,3])
        self.mates = [("getCarried",1)]
      
    def match(self, action):
        return (action.type == 'getCarried' and action.parameters[0] == self.agent.token)

    def sync(self, sender, event, params):
        if event == 'ready':     
            self.agent.remove_physical_item(sender.agent.type, 1)
            sender.agent.location = self.agent.location
            sender.agent.carried = False

class RequestDelivery(Action):
    action = ('deliverRequest',[1])
    def __init__(self, agent, game_state, parameters):
        super(RequestDelivery, self).__init__(agent, game_state, parameters, type='deliverRequest',qtd_args=[1])
        self.mates = [("deliverAgent",1)]
        self.any_time_action = True

    def match(self, action):
        if (action.type == 'deliverAgent' and action.parameters[0] == self.agent.token):
            if (self.parameters[0] == action.agent.token):
                return True
        return False

    def execute(self, map, nodes, events, tasks):
        self.mediator.notify(self, 'ready', [])       


