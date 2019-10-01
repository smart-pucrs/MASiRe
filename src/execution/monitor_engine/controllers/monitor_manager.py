import os
import time
from datetime import date
from flask import json
from monitor_engine.helpers.match import Match


class MonitorManager:

    def __init__(self, simulation_config):
        self.simulation_config = simulation_config
        self.current_match = 0
        self.current_step = 0
        self.matchs = []
        self.sim_report = None

    def create_new_match(self, map_config):
        match = Match(map_config)

        self.matchs.append(match)

    def get_next_step(self):
        match = self.matchs[self.current_match]

        if self.current_step < match.get_total_steps() - 1:
            self.current_step += 1

        step = match.get_step(self.current_step)

        return self.formatted_step(match, step)

    def get_prev_step(self):
        match = self.matchs[self.current_match]

        if self.current_step > 0:
            self.current_step -= 1

        step = match.get_step(self.current_step)

        return self.formatted_step(match, step)

    def get_next_match(self):
        if self.current_match < len(self.matchs) - 1:
            self.current_match += 1

        self.current_step = 0
        match = self.matchs[self.current_match]
        step = match.get_step(self.current_step)

        return self.formatted_match(match, step)

    def get_prev_match(self):
        if self.current_match > 0:
            self.current_match -= 1

        self.current_step = 0
        match = self.matchs[self.current_match]
        step = match.get_step(self.current_step)

        return self.formatted_match(match, step)

    def get_current_match(self):
        match = self.matchs[self.current_match]
        step = match.get_step(self.current_step)

        return self.formatted_match(match, step)

    @staticmethod
    def formatted_step(match, step):
        return {
            'total_steps': match.get_total_steps(),
            'environment': step['environment'],
            'actors': step['actors']
        }

    def formatted_match(self, match, step):
        return {
            'match_info': {'current_match': self.current_match, 'total_matchs': len(self.matchs)},
            'map_info': match.map_config,
            'step_info': self.formatted_step(match, step)
        }

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
            new_match = Match(match['map_percepts'], match['steps'], match['match_report'])
            self.matchs.append(new_match)

        self.sim_report = sim_report

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

    def get_initial_information(self):
        return {
            'sim_information': self.simulation_config,
        }
