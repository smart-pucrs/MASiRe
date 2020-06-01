from .action import Action
from ..exceptions.exceptions import *

class Move(Action):
    # __name__ = 'move'
    def __init__(self, agent, game_state, parameters):
        super(Move, self).__init__(agent, game_state, parameters, type='move',qtd_args=[1,2])

    def check_parameters(self):
        if len(self.parameters) == 1:
            if self.parameters[0] != 'cdm':
                raise FailedUnknownFacility('Unknown facility.')
   
    def check_constraints(self):
        if not self.agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')        

    def execute(self, map, nodes, events, tasks):
        if len(self.parameters) == 1:
            destination = map.cdm_location
        else:
            destination = self.parameters

        if not self.agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')

        new_location = self.agent.location
        new_route = []
        new_distance = 0
        if (map.check_location(self.agent.location, destination)):
            new_location = destination
        else:        
            new_state: dict = {}
            if not self.agent.route or not map.check_location([*self.agent.route[-1][:-1]], destination):
                result, route, distance = map.get_route(self.agent.location, destination, self.agent.abilities, self.agent.speed, nodes, events)

                if not result:
                    raise FailedNoRoute('Agent is not capable of entering Event locations.')
                else:
                    new_route = route
                    new_distance = distance
            else:
                exeption = None
                destiny = self.agent.route[0]
                if destiny[2] != map.check_coord_in_events((destiny[:-1]), events):
                    result, route, distance = self.map.get_route(self.agent.location, destination, self.agent.abilities, self.agent.speed, nodes, events)

                    if not result:
                        raise FailedNoRoute('Agent is not capable of entering Event locations.')
                    else:
                        new_route = route
                        new_distance = distance
                            
                if new_route:
                    new_location = new_route.pop(0)[:-1]
                new_distance = map.euclidean_distance(self.agent.location, destination)
                self.agent.discharge()

        self.agent.route = new_route
        self.agent.location = new_location
        self.agent.destination_distance = new_distance

        return None