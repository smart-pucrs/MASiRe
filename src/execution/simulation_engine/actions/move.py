from .action import Action
from ..exceptions.exceptions import *

class Move(Action):
   
    def __init__(self, agent, skills, resources, parameters):
        super(Move, self).__init__(agent, skills, resources, parameters, type='move',min_args=1, max_args=2)

    def check_parameters(self):
        if len(self.parameters) == 1:
            if self.parameters[0] != 'cdm':
                raise FailedUnknownFacility('Unknown facility.')
   
    def check_constraints(self):
        if not self.agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')        

    def execute(self, map, nodes, events):
        if len(self.parameters) == 1:
            destination = map.cdm_location
        else:
            destination = self.parameters

        if not self.agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')

        if (map.check_location(self.agent.location, destination)):
            return {'location': destination, 'route': [], 'destination_distance': 0}, None
        else:        
            new_state: dict = {}
            if not self.agent.route or not map.check_location([*self.agent.route[-1][:-1]], destination):
                result, route, distance = map.get_route(self.agent.location, destination, self.agent.abilities, self.agent.speed, nodes, events)

                if not result:
                    return {'route': [], 'destination_distance': 0}, FailedNoRoute('Agent is not capable of entering Event locations.')
                else:
                    return {'route': route, 'destination_distance': distance}, None
            else:
                new_state: dict = {'route': [], 'destination_distance': 0}
                exeption = None
                destiny = self.agent.route[0]
                if destiny[2] != map.check_coord_in_events((destiny[:-1]), events):
                    result, route, distance = self.map.get_route(self.agent.location, destination, self.agent.abilities, self.agent.speed, nodes, events)

                    if not result:
                        exeption = FailedNoRoute('Agent is not capable of entering Event locations.')
                    else:
                        new_state['route'] = route
                        new_state['destination_distance'] = distance

                
                if new_state['route']:
                    new_state['location'] = new_state['route'].pop(0)[:-1]
                distance = map.euclidean_distance(self.agent.location, destination)
                new_state['destination_distance'] = distance = distance
                self.agent.discharge()

                return new_state, exeption