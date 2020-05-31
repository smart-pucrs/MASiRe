from math import sqrt
from .action import Action
from ..exceptions.exceptions import FailedSocialAssetRequest

class SearchSocialAsset(Action):
    def __init__(self, agent, game_state, parameters):
        super(SearchSocialAsset, self).__init__(agent, game_state, parameters, type='searchSocialAsset',qtd_args=[1])   
        self.manager_asset = game_state.social_assets_manager     

    def check_parameters(self):   
        pass

    def check_constraints(self):        
        pass 

    def execute(self, map, nodes, events, tasks):        
        social_assets = []
        for social_asset in self.manager_asset.get_assets_markers():
            if self.check_location(self.agent.location, social_asset.location, self.parameters[0]):
                social_assets.append(social_asset)

        exec(f'self.agent.social_assets = social_assets')
        # self.agents_manager.edit(token, 'social_assets', social_assets)
        return {}, None
    
    @staticmethod
    def check_location(l1, l2, radius):
        distance = sqrt((l1[0] - l2[0]) ** 2 + (l1[1] - l2[1]) ** 2)

        return distance <= radius

class RequestSocialAsset(Action):
    def __init__(self, agent, game_state, parameters):
        super(RequestSocialAsset, self).__init__(agent, game_state, parameters, type='requestSocialAsset',qtd_args=[1])   
        self.manager_asset = game_state.social_assets_manager     

    def check_parameters(self):   
        pass

    def check_constraints(self):        
        pass 

    def execute(self, map, nodes, events, tasks):        
        for social_asset in self.manager_asset.get_assets_markers():
            if social_asset.identifier == self.parameters[0]:
                if social_asset.active:
                    for asset in self.agent.social_assets:
                        if asset.identifier == self.parameters[0]:
                            self.manager_asset.set_marker_status(self.parameters[0], False)
                            self.manager_asset.requests[self.agent.token] = self.parameters[0]
                            self.agent.social_assets.remove(asset)
                            return self.agent.token

                    raise FailedSocialAssetRequest('The agent dont know this social asset.')
                raise FailedSocialAssetRequest('The social asset is not active.')
        raise FailedSocialAssetRequest('The id given dont exits.')