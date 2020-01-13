import json
import os
import time
from datetime import date

from flask import request
from flask_restful import Resource, abort
from monitor_engine.controllers.monitor_manager import MonitorManager

monitor_manager = MonitorManager()


def record_simulation():
    current_date = date.today().strftime('%d-%m-%Y')
    hours = time.strftime("%H:%M:%S")
    file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

    abs_path = os.getcwd() + '/replays/' + file_name

    formatted_data = monitor_manager.format_simulation_data()

    with open(abs_path, 'w+') as file:
        file.write(json.dumps(formatted_data, sort_keys=False, indent=4))


def load_simulation(replay_file_name):
    replay_path = f'{os.getcwd()}/{replay_file_name}'
    replay_data = json.loads(open(replay_path, 'r').read())

    monitor_manager.load_simulation(replay_data)


class SimulationManager(Resource):
    def __init__(self, simulation_config, to_record, replay_file_name=None):
        if replay_file_name is not None:
            load_simulation(replay_file_name)
        else:
            self.to_record = to_record
            monitor_manager.set_sim_config(simulation_config)

    def get(self, id_attribute):
        if id_attribute == 'config':
            if monitor_manager.check_sim_config():
                response = monitor_manager.get_sim_config()
                return response, 200

            abort(404, message='The monitor dont have the simulation config yet.')

        elif id_attribute == 'report':
            if monitor_manager.check_sim_report():
                response = monitor_manager.get_sim_report()
                return response, 200

            abort(404, message='The monitor dont have the report of the simulation yet.')

        elif id_attribute == 'matches':
            response = dict(total_matches=monitor_manager.get_total_matches(),
                            total_steps=monitor_manager.get_total_steps())

            return response, 200

        else:
            abort(404, message=f'End point "{id_attribute}" dont exists.')

    def post(self, id_attribute):
        if id_attribute == 'config':
            try:
                json_data = request.get_json(force=True)
                monitor_manager.set_sim_config(json_data)
                return 'Ok', 200

            except Exception as e:
                abort(404, message=f'Unknown error: {str(e)}')

        elif id_attribute == 'report':
            try:
                json_data = request.get_json(force=True)
                monitor_manager.set_sim_report(json_data)

                if self.to_record:
                    record_simulation()

                return 'Ok', 200

            except Exception as e:
                abort(404, message=f'Unknown error: {str(e)}')

        abort(404, message=f'Attribute {id_attribute} is not a valid attribute.')


class MatchStepManager(Resource):
    def get(self, match, step=None):
        if monitor_manager.check_match_id(match):
            if step is not None:
                if monitor_manager.check_step_id(match, step):
                    return monitor_manager.get_match_step(match, step), 200

                abort(404, message='The current match dont have this step yet.')
            abort(404, message='The step id is required to complete this request.')
        abort(404, message='Match not found.')

    def post(self, match, step=None):
        if monitor_manager.check_match_id(match):
            if step is None:
                try:
                    json_data = request.get_json(force=True)
                    monitor_manager.add_match_step(match, json_data)
                    return 'Ok', 200

                except Exception as e:
                    abort(404, message=f'Unknown error: {str(e)}')

                abort(404, message='The current match dont have this step yet.')
            abort(404, message='Change step is not a valid operation.')
        abort(404, message='Match not found.')


class MatchInfoManager(Resource):
    def get(self, match, id_attribute):
        if monitor_manager.check_match_id(match):
            if id_attribute == 'report':
                report = monitor_manager.get_match_report(match)

                if report:
                    return report, 200

                abort(404, message=f'The Match report {match} is not available yet.')
            elif id_attribute == 'map':
                map_config = monitor_manager.get_match_map(match)

                if map_config:
                    return map_config, 200

                abort(404, messsage=f'The Match {match} doesnt have map information yet.')

            else:
                abort(404, message=f'Attribute {id_attribute} is not a valid attribute.')
        abort(404, message=f'Match not found.')

    def post(self, match, id_attribute):
        if id_attribute == 'report':
            try:
                json_data = request.get_json(force=True)
                monitor_manager.set_match_report(match, json_data)
                return 'Ok', 200

            except Exception as e:
                abort(404, message=f'Unknown error: {str(e)}')

        elif id_attribute == 'map':
            try:
                json_data = request.get_json(force=True)
                monitor_manager.add_match(json_data)
                return 'Ok', 200

            except Exception as e:
                abort(404, message=f'Unknown error: {str(e)}')

        else:
            abort(404, message=f'Attribute {id_attribute} is not a valid attribute.')
        abort(404, message='Match not found.')
