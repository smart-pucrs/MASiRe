from .action import Action
from ..simulation_helpers.report import Report 
from ..exceptions.exceptions import FailedLocation, FailedItemAmount

class CollectWater(Action):   
    def __init__(self, agent, game_state, parameters):
        super(CollectWater, self).__init__(agent, game_state, parameters, type='collectWater', qtd_args=[0])        

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

class TakePhoto(Action):   
    def __init__(self, agent, game_state, parameters):
        super(TakePhoto, self).__init__(agent, game_state, parameters, type='takePhoto', qtd_args=[0])        

    def check_parameters(self):   
        pass

    def check_constraints(self):        
        pass 

    def execute(self, map, nodes, events, tasks):                
        for photo in tasks['photos']:
            if map.check_location(photo.location, self.agent.location):
                photo.active = False
                report = Report()
                report.photos.collected = 1
                self.agent.add_virtual_item(photo)            
                return None
        raise FailedLocation('The agent is not in a location with a photograph event.')

class AnalyzePhoto(Action):   
    def __init__(self, agent, game_state, parameters):
        super(AnalyzePhoto, self).__init__(agent, game_state, parameters, type='analyzePhoto', qtd_args=[0])        
        self.game_state = game_state
    def check_parameters(self):   
        pass

    def check_constraints(self):        
        if len(self.agent.virtual_storage_vector) == 0:
            raise FailedItemAmount('The agent has no photos to analyze.')

    def execute(self, map, nodes, events, tasks):     
        report = Report()
        photo_identifiers = []
        victim_identifiers = []
        for photo in self.agent.virtual_storage_vector:
            for victim in photo.victims:
                victim_identifiers.append(victim.identifier)
            report.photos.analysed = 1
            photo_identifiers.append(photo.identifier)

        for photo in tasks['photos']:
            if photo.identifier in photo_identifiers:
                photo_identifiers.remove(photo.identifier)
                photo.analyzed = True
                for victim in photo.victims:
                    victim.active = True
                    self.game_state.steps[self.game_state.current_step]['victims'].append(victim)
        
        self.agent.clear_virtual_storage()
        return None

