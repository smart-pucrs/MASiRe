from .action import Action
from ..simulation_helpers.report import Report 
from ..exceptions.exceptions import FailedLocation

class CollectWater(Action):   
    def __init__(self, agent, skills, resources, parameters):
        super(CollectWater, self).__init__(agent, skills, resources, parameters, type='collectWater',min_args=0, max_args=0)        

    def check_parameters(self):   
        pass

    def check_constraints(self):        
        pass 

    def execute(self, map, nodes, events, tasks):        
        for t in tasks['water_samples']:                         
            if not t.active and map.check_location(t.location, self.agent.location):
                t.active = False
                report = Report()
                report.samples.collected = 1
                self.agent.add_physical_item(t)
                return {}, None

        raise FailedLocation('The agent is not in a location with a water sample event.')
