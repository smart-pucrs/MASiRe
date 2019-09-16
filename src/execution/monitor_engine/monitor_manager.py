import os
import time
from datetime import date

from flask import json


class MonitorManager:

    def __init__(self):
        self.current_match = 0
        self.monitor_match = 0
        self.current_step = 0
        self.simulation_info = {}
        self.matchs = []

    def init_replay_mode(self, replay):
        replay_path = os.getcwd() + '/replays/' + replay

        replay_data = json.loads(open(replay_path, 'r').read())
            
        self.simulation_info = replay_data['simulation_info']
        self.matchs = replay_data['matchs']
    
    def init_live_mode(self, config):
        config_location = os.getcwd() + '/' + config
        maps = json.load(open(config_location, 'r'))['map']['maps']

        for map_info in maps:
            self.matchs.append({'map': map_info, 'steps_data': []})

    def set_simulation_info(self, simulation_info):
        self.simulation_info = simulation_info

    def save_replay(self):
        current_date = date.today().strftime('%d-%m-%Y')
        hours = time.strftime("%H:%M:%S")
        file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

        abs_path = os.getcwd() + '/replays/'
        replay_data = {'simulation_info': self.simulation_info, 'matchs': self.matchs}

        with open(str(abs_path + file_name), 'w+') as file:
            file.write(json.dumps(replay_data, sort_keys=False, indent=4))

    def get_initial_information(self):
        map_info = self.matchs[self.monitor_match]['map']

        total_matchs = len(self.matchs)
        match_info = {'current_match': self.current_match, 'total_matchs': total_matchs}

        return {
            'simulation_info': self.simulation_info,
            'map_info': self.matchs[self.monitor_match]['map'],
            'match_info': match_info
        }

    def next_match_api(self):
        self.current_match += 1

    def add_step_data(self, step_data):
        self.matchs[self.current_match]['steps_data'].append(step_data)

    def next_step(self):
        total_steps = len(self.matchs[self.monitor_match]['steps_data'])
        
        if self.current_step == total_steps-1:
            return self.get_step_data()

        self.current_step += 1
        return self.get_step_data()

    def prev_step(self):
        if self.current_step == 0:
            return self.get_step_data()

        self.current_step -= 1
        return self.get_step_data()

    def prev_match(self):
        if self.current_match == 0:
            self.current_step = 0

            return self.get_match_data()

        else:
            self.monitor_match -= 1
            self.current_step = 0

            return self.get_match_data()



    def next_match(self):
        if self.monitor_match == len(self.matchs)-1:
            self.current_step = 0

            return self.get_match_data()

        else:
            self.monitor_match += 1
            self.current_step

            return self.get_match_data()
            
    def get_step_data(self):
        step = self.current_step
        step_data = self.matchs[self.monitor_match]['steps_data'][step]
        total_steps = len(self.matchs[self.monitor_match]['steps_data'])
        
        return {'current_step': step,
                'total_steps': total_steps,
                'step_data': step_data}

    def get_match_data(self):
        step = self.current_step
        total_matchs = len(self.matchs)
        current_match = self.monitor_match
        map_info = self.matchs[current_match]['map']
        total_steps = len(self.matchs[current_match]['steps_data'])
        step_data = self.matchs[current_match]['steps_data'][step]

        return {
            'match_info': {
                'current_match': current_match,
                'total_matchs': total_matchs
            },
            'step_info': {
                'step': step,
                'total_steps': total_steps,
                'step_data': step_data,    
            },
            'map_info': map_info
        }