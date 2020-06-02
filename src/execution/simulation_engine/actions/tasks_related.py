from .action import Action
from ..simulation_helpers.report import Report 
from ..exceptions.exceptions import FailedLocation, FailedItemAmount

class CollectWater(Action):   
    action = ('collectWater',[0])
    def __init__(self, agent, game_state, parameters):
        super(CollectWater, self).__init__(agent, game_state, parameters, type='collectWater', qtd_args=[0])        

    def check_parameters(self):   
        pass

    def check_constraints(self,map):        
        pass 

    def execute(self, map, nodes, events, tasks):        
        for t in tasks['water_samples']:                         
            if map.check_location(t.location, self.agent.location):
                t.active = False
                report = Report()
                report.samples.collected = 1
                self.agent.add_physical_item(t)
                return {}, None

        raise FailedLocation('The agent is not in a location with a water sample event.')

class TakePhoto(Action):   
    action = ('takePhoto',[0])
    def __init__(self, agent, game_state, parameters):
        super(TakePhoto, self).__init__(agent, game_state, parameters, type='takePhoto', qtd_args=[0])        

    def check_parameters(self):   
        pass

    def check_constraints(self,map):        
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
    action = ('analyzePhoto',[0])
    def __init__(self, agent, game_state, parameters):
        super(AnalyzePhoto, self).__init__(agent, game_state, parameters, type='analyzePhoto', qtd_args=[0])        
        self.game_state = game_state
    def check_parameters(self):   
        pass

    def check_constraints(self,map):        
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

class RescueVictim(Action):   
    action = ('rescueVictim',[0])
    def __init__(self, agent, game_state, parameters):
        super(RescueVictim, self).__init__(agent, game_state, parameters, type='rescueVictim', qtd_args=[0])        

    def check_parameters(self):   
        pass

    def check_constraints(self,map):        
        pass 

    def execute(self, map, nodes, events, tasks):               
        report = Report()

        for victim in tasks['victims']:
            if map.check_location(victim.location, self.agent.location):
                victim.active = False
                    
                if (victim.lifetime <= 0): report.victims.dead = 1
                else: report.victims.alive = 1

                self.agent.add_physical_item(victim)
                return None

        for photo in tasks['photos']:
            for victim in photo.victims:
                if map.check_location(victim.location, self.agent.location):
                    victim.active = False
                    self.agent.add_physical_item(victim)
                    return None

        raise FailedLocation('No victim by the given location is known.')

