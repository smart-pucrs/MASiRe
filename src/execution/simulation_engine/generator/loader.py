import random
import json
from simulation_engine.simulation_objects.flood import Flood
from simulation_engine.simulation_objects.photo import Photo
from simulation_engine.simulation_objects.victim import Victim
from simulation_engine.simulation_objects.water_sample import WaterSample

from simulation_engine.simulation_objects.social_asset_marker import SocialAssetMarker
from simulation_engine.generator.genarator_base import GeneratorBase
import simulation_engine.simulation_helpers.events_formatter as formatter
import copy

class Loader(GeneratorBase):
    """Class that generate all the events step, by step or separated if needed."""

    def __init__(self, config, map, path_to_events):
        super(Loader, self).__init__(config, map)
        self.events = json.load(open(path_to_events, 'r'))

    def generate_events(self, map) -> list:
        template = dict(step=-1, flood=None, victims=[], photos=[], water_samples=[],propagation=[])
        events: list = [template] * self.events['map']['steps']


        steps = iter(self.events['matchs'][0]['steps'])
        # for idx, step in enumerate(self.events['matchs'][0]['steps']):
        for step in steps:
            
            sim_step = dict(step=-1,flood=None, victims=[], photos=[], water_samples=[],propagation=[])

            if step is not None:
                idx = step['step']
                # sim_step['flood'] = Flood(step['flood'])
                # print("Teste: ", sim_step['flood'].__dict__)
                # sim_step['flood'] = Flood(step['flood']['identifier'], step['flood']['period'], step['flood']['keeped'],
                #                           step['flood']['dimensions'], step['flood']['list_of_nodes'])
                nodes = self.get_nodes(step['flood']['dimensions']['location'],step['flood']['dimensions']['shape'],step['flood']['dimensions']['radius'])
                (max_propagation, propagation_per_step, nodes_propagation, propagation) = self.generate_propagation(step['flood']['propagation2'], step['flood']['dimensions'], nodes, map)
                
                sim_step['step'] = step['step']
                sim_step['flood'] = Flood(step['flood']['identifier'], step['flood']['period'], step['flood']['keeped'],
                                          step['flood']['dimensions'], nodes, max_propagation, propagation_per_step, step['flood']['propagation2']['victimProbability'], nodes_propagation)
                # sim_step['propagation'] = propagation
                self.flood_id += 1

                sim_step['victims'] = [Victim(victim['flood_id'], victim['identifier'], victim['size'], victim['lifetime'],
                                              victim['location'], victim['in_photo']) for victim in step['victims']]
                self.victim_id += len(sim_step['victims'])

                sim_step['propagation']: [Victim(victim['flood_id'], victim['identifier'], victim['size'], victim['lifetime'],
                                              victim['location'], victim['in_photo']) for victim in step['propagation']]
                self.victim_id += len(sim_step['victims'])

                photos = []
                for photo in step['photos']:
                    victims_in_photo = [Victim(victim['flood_id'], victim['identifier'], victim['size'],
                                               victim['lifetime'], victim['location'], victim['in_photo'])
                                        for victim in photo['victims']]
                    self.victim_id += len(victims_in_photo)

                    photos.append(Photo(photo['flood_id'], photo['identifier'], photo['size'], victims_in_photo,
                                        photo['location']))

                sim_step['photos'] = photos
                self.photo_id += len(photos)

                sim_step['water_samples'] = [WaterSample(sample['flood_id'], sample['identifier'], sample['size'],
                                             sample['location']) for sample in step['water_samples']]
                self.water_sample_id += len(sim_step['water_samples'])

                events[idx] = sim_step
        return events

    def generate_social_assets(self) -> list:
        social_assets: list = [0] * len(self.events['matchs'][0]['social_assets'])

        for idx, asset in enumerate(self.events['matchs'][0]['social_assets']):
            social_assets[idx] = SocialAssetMarker(asset['identifier'], asset['location'],
                                                   asset['profession'], asset['abilities'], asset['resources'])

        return social_assets

    @staticmethod
    def write_first_match(config, steps, social_assets, generator, file_name):
        config_copy = copy.deepcopy(config)
        del config_copy['generate']
        del config_copy['socialAssets']
        del config_copy['agents']
        del config_copy['actions']

        match = dict(steps=Loader.get_json_events(steps),
                     social_assets=generator.get_json_social_assets(social_assets.social_assets_markers))

        config_copy['matchs'] = [match]

        with open(file_name, 'w+') as file:
            file.write(json.dumps(config_copy, sort_keys=False, indent=4))

    def write_match(self, generator, file_name):
        with open(file_name, 'r') as file:
            config = json.loads(file.read())

        match = dict(steps=generator.get_json_events(self.steps),
                     social_assets=generator.get_json_social_assets(self.social_assets_manager.social_assets_markers))

        config['matchs'].append(match)

        with open(file_name, 'w') as file:
            file.write(json.dumps(config, sort_keys=False, indent=4))

    @staticmethod
    def get_json_events(events):
        json_events = []

        for event in events:
            events_dict = None

            if event['flood'] is not None:
                events_dict = dict()
                events_dict['step'] = event['step']
                events_dict['flood'] = formatter.format_flood(event['flood'])
                events_dict['victims'] = formatter.format_victims(event['victims'])
                events_dict['photos'] = formatter.format_photos(event['photos'])
                events_dict['water_samples'] = formatter.format_water_samples(event['water_samples'])
                if len(event['propagation']) >= 1:
                    events_dict['propagation'] = formatter.format_victims(event['propagation'][0])
                else:
                    events_dict['propagation'] = []
            json_events.append(events_dict)

        return json_events