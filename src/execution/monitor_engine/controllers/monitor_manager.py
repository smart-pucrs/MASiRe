import os
import time
from datetime import date
from flask import json
from monitor_engine.helpers.match import Match


class MonitorManager:

    def __init__(self, simulation_config):
        self.simulation_config = simulation_config
        self.current_match = 0
        self.matchs = []
        self.sim_report = None

    def create_new_match(self, map_config):
        match = Match(map_config)

        self.matchs.append(match)

    def add_percepts(self, actors, environment):
        match = self.matchs[-1]

        step = {'actors': actors, 'environment': environment}
        match.add_step(step)

    def add_match_report(self, match_report):
        match = self.matchs[-1]
        match.report = match_report

    def add_simulation_report(self, sim_report):
        self.sim_report = sim_report

    def load_simulation(self, matchs, sim_report):
        for match in matchs:
            new_match = Match(match['map_config'], match['steps'], match['match_report'])
            self.matchs.append(new_match)

        self.sim_report = sim_report

    def record_simulation(self):
        current_date = date.today().strftime('%d-%m-%Y')
        hours = time.strftime("%H:%M:%S")
        file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

        abs_path = os.getcwd() + '/replays/'
        formatted_data = self.format_simulation_data()

        with open(str(abs_path + file_name), 'w+') as file:
            file.write(json.dumps(formatted_data, sort_keys=False, indent=4))

    def format_simulation_data(self):
        simulation_config = self.simulation_config
        sim_report = self.sim_report
        matchs = []

        for match in self.matchs:
            jsonify_match = {'map_percepts': match.map_config,
                             'steps': match.steps,
                             'match_report': match.report}

            matchs.append(jsonify_match)

        formatted_data = {
            'simulation_config': simulation_config,
            'matchs': matchs,
            'sim_report': sim_report
        }

        return formatted_data
