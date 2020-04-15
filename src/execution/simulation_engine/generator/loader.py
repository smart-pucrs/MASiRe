import random
import json
import copy
from simulation_engine.simulation_objects.flood import Flood
from simulation_engine.simulation_objects.photo import Photo
from simulation_engine.simulation_objects.victim import Victim
from simulation_engine.simulation_objects.water_sample import WaterSample

from simulation_engine.simulation_objects.social_asset_marker import SocialAssetMarker
from simulation_engine.generator.genarator_base import GeneratorBase
import simulation_engine.simulation_helpers.events_formatter as formatter
from ..simulation_objects.event import Event


class Loader(GeneratorBase):
    """Class that generate all the events step, by step or separated if needed."""

    def __init__(self, config, map, path_to_events):
        super(Loader, self).__init__(config, map)
        events_file = json.load(open(path_to_events, 'r'))
        self.number_steps = events_file['map']['steps']
        self.events = events_file['matchs'][0]['steps']
        self.social_assets = events_file['matchs'][0]['social_assets']

    def generate_events(self, map) -> list:
        template = dict(step=-1, flood=None, victims=[], photos=[], water_samples=[],propagation=[])
        # events: list = [template.copy()] * self.number_steps
        events: list = [template.copy() for i in range(self.number_steps)]

        for e in iter(self.events):  
            if e is None: 
                continue          
            e_obj = self.__prepare_event(e)
            e_obj.affect_map(map, self)

            sim_step = events[e_obj.step]
            sim_step['step'] = e['step']
            sim_step['flood'] = e_obj
            sim_step['victims'] = [Victim(**victim, photo=False) for victim in e['victims']]
            # sim_step['propagation'] = [Victim(**victim, photo=False) for victim in e['propagation']]
            sim_step['propagation'] = [[Victim(**victim, photo=False) for victim in s] for s in e['propagation']]

            photos = []
            for photo in e['photos']:
                victims_in_photo = [Victim(**victim, photo=True) for victim in photo['victims']]

                photos.append(Photo(photo['flood_id'], photo['identifier'], photo['size'], victims_in_photo,
                                    photo['location']))
            sim_step['photos'] = photos

            sim_step['water_samples'] = [WaterSample(**sample) for sample in e['water_samples']]
        return events

    def __prepare_event(self, info):
        config = {}
        config['step'] = info['step']
        config['id'] = info['flood']['id']
        config['end'] = info['flood']['end']
        config['dimension'] = info['flood']['dimension']
        config['propagation'] = info['flood']['propagation']
        return Event(**config)

    def generate_social_assets(self) -> list:
        social_assets: list = [0] * len(self.social_assets)

        for idx, asset in enumerate(self.social_assets):
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
                     social_assets=generator.get_json_social_assets(social_assets))

        config_copy['matchs'] = [match]

        with open(file_name, 'w+') as file:
            file.write(json.dumps(config_copy, sort_keys=False, indent=4, default=lambda o: o.dict()))

    def write_match(self, generator, file_name):
        with open(file_name, 'r') as file:
            config = json.loads(file.read())

        match = dict(steps=generator.get_json_events(self.steps),
                     social_assets=generator.get_json_social_assets(self.social_assets_manager.social_assets_markers))

        config['matchs'].append(match)

        with open(file_name, 'w') as file:
            file.write(json.dumps(config, sort_keys=False, indent=4, default=lambda o: o.__dict__))

    @staticmethod
    def get_json_events(events):
        json_events = []

        for event in events:
            events_dict = None

            if event['flood'] is not None:
                events_dict = dict()
                events_dict['step'] = event['step']
                events_dict['flood'] = event['flood'].dict()
                events_dict['victims'] = formatter.format_victims(event['victims'])
                events_dict['photos'] = formatter.format_photos(event['photos'])
                events_dict['water_samples'] = formatter.format_water_samples(event['water_samples'])
                if len(event['propagation']) >= 1:
                    prop = []
                    for s in range(len(event['propagation'])):
                        prop.append(formatter.format_victims(event['propagation'][s]))
                    events_dict['propagation'] = prop
                else:
                    events_dict['propagation'] = []
                json_events.append(events_dict)

        return json_events