import random
import simulation_engine.simulation_helpers.events_formatter as formatter

# from simulation_engine.simulation_objects.flood import Flood
# from simulation_engine.simulation_objects.photo import Photo
# from simulation_engine.simulation_objects.victim import Victim
# from simulation_engine.simulation_objects.water_sample import WaterSample
# from simulation_engine.simulation_objects.social_asset_marker import SocialAssetMarker

from abc import ABCMeta, abstractmethod

class GeneratorBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_events(self, map) -> list:
        raise NotImplementedError("Must override to generate events")

    @abstractmethod
    def generate_social_assets(self) -> list:
        raise NotImplementedError("Must override to social assets options")

    # TODO: fix this to any shape 
    def get_nodes(self, position, shape, radius, map)-> list:
        if shape == 'circle':
            list_of_nodes: list = map.nodes_in_radius(position, radius)
        return list_of_nodes

    def generate_propagation(self, epicentre, radius, maximum, perStep, nodes, map) -> (float,float,list,list):
        if (perStep == 0):
            return []
        nodes_propagation: list = []        
        old_nodes: list = nodes

        maximun_radius = ((maximum / 100)+1) * radius
        increase_perStep = perStep / 100 * radius

        until = range(int(maximum / perStep))
        for prop in until:
            new_nodes = map.nodes_in_radius(epicentre, radius + increase_perStep * prop)
            difference = self.get_difference(old_nodes, new_nodes)

            nodes_propagation.append(difference)
            old_nodes = new_nodes
        return nodes_propagation

    def get_difference(self, node_list1, node_list2):
        return [node for node in node_list1 if node in node_list2]

    @staticmethod
    def get_json_social_assets(social_assets):
        return formatter.format_assets(social_assets)
