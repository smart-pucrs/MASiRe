import copy
import datetime
import json
import pathlib
import logging
import glob
from math import sqrt

from ..exceptions.exceptions import *
from simulation_engine.generator.generator import Generator
from simulation_engine.generator.loader import Loader
# from simulation_engine.loader.loader import Loader
from simulation_engine.simulation_helpers.agents_manager import AgentsManager
from simulation_engine.simulation_helpers.map import Map
from simulation_engine.simulation_helpers.social_assets_manager import SocialAssetsManager
from simulation_engine.simulation_helpers.report import Report 
from ..actions.action import *
from ..actions.move import *
from ..actions.deliver_virtual import *
from ..actions.deliver_physical import *
from ..actions.tasks_related import *
from ..actions.request import *
from ..actions.carry import *

logger = logging.getLogger(__name__)

class Cycle:
    def __init__(self, config, load_sim, write_sim):
        self.map = Map(config['map']['maps'][0], config['map']['proximity'], config['map']['movementRestrictions'])
        self.actions = config['actions']
        self.max_steps = config['map']['steps']
        self.cdm_location = (config['map']['maps'][0]['centerLat'], config['map']['maps'][0]['centerLon'])
        self.agents_manager = AgentsManager(config['agents'], self.cdm_location)

        if load_sim:
            path_to_events = pathlib.Path(__file__).parents[4] / config['map']['maps'][0]['events']
            generator = Loader(config, self.map, path_to_events)
        else:
            generator = Generator(config, self.map)

        self.steps = generator.generate_events(self.map)
        self.social_assets_manager = SocialAssetsManager(config['map'], config['socialAssets'],
                                                         generator.generate_social_assets())
        self.agents_manager.assets = self.social_assets_manager

        if write_sim:
            hour = datetime.datetime.now().hour
            minute = datetime.datetime.now().minute
            sim_id = config['map']['id']
            path = pathlib.Path(__file__).parents[4] / 'files'

            hour = '{:0>2d}'.format(hour)
            minute = '{:0>2d}'.format(minute)

            self.sim_file = str((path / f'Auto_Generate_Config_File_{sim_id}_at_{hour}h_{minute}min.txt'))
            Loader.write_first_match(config, self.steps, self.social_assets_manager.social_assets_markers, generator, self.sim_file)

        self.map_percepts = config['map']
        # self.max_floods = generator.flood_id
        # self.max_victims = generator.victim_id
        # self.max_photos = generator.photo_id
        # self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.match_history = []

    def restart(self, config, load_sim, write_sim):
        self.map.restart(config['map']['maps'][0], config['map']['proximity'], config['map']['movementRestrictions'])

        if load_sim:
            generator = Loader(config)
        else:
            generator = Generator(config, self.map)

        self.steps = generator.generate_events(self.map)
        self.social_assets_manager = SocialAssetsManager(config['map'], config['socialAssets'],
                                                         generator.generate_social_assets())

        if write_sim:
            self.write_match(generator, self.sim_file)

        self.map_percepts = config['map']
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.max_steps = config['map']['steps']
        self.cdm_location = (config['map']['maps'][0]['centerLat'], config['map']['maps'][0]['centerLon'])
        self.agents_manager.restart(config['agents'], self.cdm_location)

    # def write_first_match(self, config, generator, file_name):
    #     config_copy = copy.deepcopy(config)
    #     del config_copy['generate']
    #     del config_copy['socialAssets']
    #     del config_copy['agents']
    #     del config_copy['actions']

    #     match = dict(steps=generator.get_json_events(self.steps),
    #                  social_assets=generator.get_json_social_assets(self.social_assets_manager.social_assets_markers))

    #     config_copy['matchs'] = [match]

    #     with open(file_name, 'w+') as file:
    #         file.write(json.dumps(config_copy, sort_keys=False, indent=4))

    def write_match(self, generator, file_name):
        with open(file_name, 'r') as file:
            config = json.loads(file.read())

        match = dict(steps=generator.get_json_events(self.steps),
                     social_assets=generator.get_json_social_assets(self.social_assets_manager.social_assets_markers))

        config['matchs'].append(match)

        with open(file_name, 'w') as file:
            file.write(json.dumps(config, sort_keys=False, indent=4))

    def connect_agent(self, token):
        return self.agents_manager.connect(token)

    def connect_social_asset(self, main_token, token):
        if main_token not in self.agents_manager.get_tokens():
            raise Exception(f'"{main_token}" token not exists.')

        if main_token not in self.social_assets_manager.requests.keys():
            raise Exception(f'"{main_token}" dont request a social asset.')

        social_asset_id = self.social_assets_manager.requests[main_token]
        social_asset = None
        for temp in self.social_assets_manager.get_assets_markers():
            if temp.identifier == social_asset_id:
                social_asset = temp
                break

        del self.social_assets_manager.requests[main_token]
        return self.social_assets_manager.connect(token, social_asset.identifier, social_asset.profession)

    def disconnect_agent(self, token):
        return self.agents_manager.disconnect(token)

    def disconnect_social_asset(self, token):
        return self.social_assets_manager.disconnect(token)

    def get_agents_info(self):
        return self.agents_manager.get_info()

    def get_active_agents_info(self):
        return self.agents_manager.get_active_info()

    def get_assets_info(self):
        return self.social_assets_manager.get_info()

    def get_assets_tokens(self):
        return self.social_assets_manager.get_tokens()

    def get_active_assets_info(self):
        return self.social_assets_manager.get_active_info()

    def get_step(self):
        events = []
        for step in self.steps[:(self.current_step+1)]:
            if step['flood']:
                if step['flood'].active:
                    events.append(step['flood'])

                    for victim in step['victims']:
                        if victim.active:
                            events.append(victim)

                    for photo in step['photos']:
                        if photo.active:
                            events.append(photo)

                    for water_sample in step['water_samples']:
                        if water_sample.active:
                            events.append(water_sample)

        return events

    def get_previous_steps(self):
        previous_steps = []
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                previous_steps.append(self.steps[i])

        return previous_steps

    def activate_step(self):
        if self.steps[self.current_step]['flood'] is None:
            return

        self.steps[self.current_step]['flood'].active = True

        for victim in self.steps[self.current_step]['victims']:
            victim.active = True

        for water_sample in self.steps[self.current_step]['water_samples']:
            water_sample.active = True

        for photo in self.steps[self.current_step]['photos']:
            photo.active = True

    def check_steps(self):
        return self.current_step == self.max_steps

    def update_steps(self):
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue
            
            if self.steps[i]['propagation']:
                new_victims = self.steps[i]['propagation'].pop(0)
                for victim in new_victims:
                    victim.active = True

                self.steps[i]['victims'].extend(new_victims)

            if self.steps[i]['flood'].keeped:
                self.steps[i]['flood'].update_state()

                if self.steps[i]['flood'].active:
                    finished = True

                    for victim in self.steps[i]['victims']:
                        if victim.active:
                            finished = False
                            victim.lifetime -= 1

                    for photo in self.steps[i]['photos']:
                        if photo.active:
                            finished = False

                        for victim in photo.victims:
                            if victim.active:
                                finished = False
                                victim.lifetime -= 1

                            elif not photo.analyzed:
                                finished = False

                    for water_sample in self.steps[i]['water_samples']:
                        if water_sample.active:
                            finished = False
                            break

                    if finished:
                        self.steps[i]['flood'].active = False

            elif self.steps[i]['flood'].active:
                self.steps[i]['flood'].update_state()

                if not self.steps[i]['flood'].active:
                    for victim in self.steps[i]['victims']:
                        victim.active = False

                    for water_sample in self.steps[i]['water_samples']:
                        water_sample.active = False

                    for photo in self.steps[i]['photos']:
                        photo.active = False

                        for victim in photo.victims:
                            victim.active = False

                else:
                    for victim in self.steps[i]['victims']:
                        if victim.active:
                            victim.lifetime -= 1

                    for photo in self.steps[i]['photos']:
                        for victim in photo.victims:
                            if victim.active:
                                victim.lifetime -= 1

    def finish_social_assets_connections(self, tokens):
        result = []

        for token in tokens:
            agent = self.social_assets_manager.get(token)
            if agent is not None:
                result.append(agent)

        self.social_assets_manager.finish_connections()

        return result

    def execute_actions(self, token_action_dict):
        requests = []
        action_results = []
        sync_actions = []        

        nodes = []
        events = []
        # tasks = {k:v for (k,v) in self.steps if k == 'water_sample' and len(v) > 0}
        tasks = {}
        tasks['water_samples'] = [w for e in self.steps for w in e['water_samples'] if w.active]
        tasks['victims'] = [w for e in self.steps for w in e['victims'] if w.active]
        tasks['photos'] = [w for e in self.steps for w in e['photos'] if w.active]
        # tasks['water_samples'] = ((w for w in e['water_samples'] if not w.active) for e in self.steps )
        for i in range(self.current_step+1):
            if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                nodes.extend(self.steps[i]['flood'].nodes)
                events.append(self.steps[i]['flood'].dimension)
        
        for token_action_param in token_action_dict:
            token, action, parameters = token_action_param.values()
            action_obj = Action.create_action(self.agents_manager.get(token),action,self,parameters)            
            if not action_obj.is_ok: 
                action_results.append(action_obj.result)
            else:
                if action_obj.need_sync:
                    matched = False
                    for acts in sync_actions:
                        if any(map(action_obj.match, acts)):
                            acts.append(action_obj)
                            matched = True
                    if (not matched):
                        sync_actions.append([action_obj])
                else:                    
                    req = action_obj.do(self.map, nodes, events, tasks)
                    if req is not None:
                        requests.append(req)
                    action_results.append(action_obj.result)

        for paired_actions in sync_actions:
            sync = SyncActions(*paired_actions)
            sync.sync(self.map, nodes, events, tasks)
            action_results.extend(sync.results())

        logger.debug(f'actions processed: {len(action_results)}')
        return action_results, requests

    # if action_name == 'inactive':
    #         self.agents_manager.edit(token, 'last_action', 'pass')
    #         self.agents_manager.edit(token, 'last_action_result', 'inactive')
    #         return {'agent': self.agents_manager.get(token), 'message': 'Agent did not send any action.'}
 
    def calculate_route(self, parameters):
        """Return the route calculated with the parameters given.

        :param parameters: Dict with the parameters to calculate the route.
        :return dict: Dictionary with the result of the operation, the route calculated, the distance od the route and
        a message."""

        response = dict(operation_result='success', route=[], distance=0, message='')

        try:
            if len(parameters) != 6:
                raise FailedWrongParam('More or less than 6 parameter was given.')

            if parameters[4] not in self.map.movement_restrictions.keys():
                raise FailedParameterType('The parameter "movement_type" is not a movement type valid.')

            if parameters[5] <= 0:
                raise FailedParameterType('The parameter "speed" can not be less or equal to 0.')

            start = [parameters[0], parameters[1]]
            end = [parameters[2], parameters[3]]
            nodes = []
            events = []

            for i in range(self.current_step):
                if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                    nodes.extend(self.steps[i]['flood'].list_of_nodes)
                    events.append(self.steps[i]['flood'].dimensions)

            result, route, distance = self.map.get_route(start, end, [parameters[4]], parameters[5], nodes, events)

            if result:
                response['operation_result'] = 'success'
                response['route'] = route
                response['distance'] = distance

            else:
                response['operation_result'] = 'noRoute'

        except FailedParameterType as e:
            response['operation_result'] = e.identifier
            response['message'] = e.message

        except Exception as e:
            response['operation_result'] = 'unknownError'
            response['message'] = str(e)

        return response

    @staticmethod
    def check_location(l1, l2, radius):
        """Verify if the first location it's close to the second location by the given radius

        :param l1: The main location to compare
        :param l2: The target location to compare
        :param radius: The radius to compare
        :return: True if is close, otherwise False
        """
        distance = sqrt((l1[0] - l2[0]) ** 2 + (l1[1] - l2[1]) ** 2)

        return distance <= radius

    def get_map_percepts(self):
        """Get the constants information about the map.

        :return dict: constants attributes of the map in config file"""

        percepts = {'proximity': self.map_percepts['proximity'], 'minLat': self.map_percepts['maps'][0]['minLat'],
                    'maxLat': self.map_percepts['maps'][0]['maxLat'], 'minLon': self.map_percepts['maps'][0]['minLon'],
                    'maxLon': self.map_percepts['maps'][0]['maxLon'],
                    'centerLat': self.map_percepts['maps'][0]['centerLat'],
                    'centerLon': self.map_percepts['maps'][0]['centerLon'],
                    'osm': self.map_percepts['maps'][0]['osm'],
                    'name': self.map_percepts['maps'][0]['name']}

        return percepts

    def match_report(self):
        """Generate a report with the completed event of each agent in the simulation

        :return dict: Dictionary with the tokens and the reports
        """
        report = {}
        tokens = [*self.agents_manager.get_tokens(), *self.social_assets_manager.get_tokens()]

        for token in tokens:
            report[token] = {'total_victims': 0, 'total_photos': 0, 'total_water_samples': 0}

            for event in self.delivered_items:
                if event['token'] == token:
                    if event['kind'] == 'victim':
                        report[token]['total_victims'] += len(event['items'])
                    elif event['kind'] == 'photo':
                        report[token]['total_photos'] += len(event['items'])
                    elif event['kind'] == 'water_sample':
                        report[token]['total_water_samples'] += len(event['items'])

        self.match_history.append(report)

        return report

    def simulation_report(self):
        """Generate a report with all match of each agent

        :return dict: Dictionary with the tokens and the reports
        """
        try:
            report = {}
            tokens = [*self.agents_manager.get_tokens(), *self.social_assets_manager.get_tokens()]

            for token in tokens:
                report[token] = {}

                report[token] = {'total_victims': 0, 'total_photos': 0, 'total_water_samples': 0}

                for match in self.match_history:
                    if token in match:
                        report[token]['total_victims'] += match[token]['total_victims']
                        report[token]['total_photos'] += match[token]['total_photos']
                        report[token]['total_water_samples'] += match[token]['total_water_samples']

        except Exception as e:
            return str(e)

        return report
