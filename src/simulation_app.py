"""
This module was made to replace the singleton used previously,
creating another layer of communication, this one between the API and the simulation.

To go back to the previous version, one must import the listeners and the simulation singleton in this file
making the appropriate changes to the file to create a socket server
Also, one file to start the app is needed, check previous versions of the repo looking after the file
"start_simulation.py"
"""
import json
import sys
import copy
import requests
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS
from simulation.simulation import Simulation
from waitress import serve

config_path, base_url, port, api_port = sys.argv[1:]


def start_instance(path):
    with open(path, 'r') as simulation_config:
        json_config = json.loads(simulation_config.read())
        return Simulation(json_config)


app = Flask(__name__)

simulation = start_instance(config_path)
initial_percepts = simulation.start()


@app.route('/register_agent', methods=['POST'])
def register_agent():
    if request.remote_addr != base_url:
        return jsonify(message='This endpoint can not be accessed.')

    agent_info = request.get_json(force=True)
    agent = simulation.create_agent(agent_info['token'], agent_info['agent_info']).json()

    map_percepts = copy.deepcopy(initial_percepts[0])
    events = copy.deepcopy(initial_percepts[1])

    for event in events:
        if event == 'flood' and events[event]:
            events[event] = events[event].json()
        else:
            events[event] = [event.json() for event in events[event]]

    return jsonify({'agent': agent, 'initial_percepts': [map_percepts, events]})


@app.route('/do_actions', methods=['POST'])
def do_actions():
    if request.remote_addr != base_url:
        return jsonify(message='This endpoint can not be accessed.')

    actions = request.get_json(force=True)

    result = copy.deepcopy(simulation.do_step(actions))

    if isinstance(result, str):
        return jsonify(result)

    if result['action_results']:
        for agent in result['action_results']:
            agent[1]['virtual_storage_vector'] = \
                [virtual.json() for virtual in agent[1]['virtual_storage_vector']]

            agent[1]['physical_storage_vector'] = \
                [physical.json() for physical in agent[1]['physical_storage_vector']]

            agent[1]['social_assets'] = \
                [asset.json() for asset in agent[1]['social_assets']]
            locations = []
            for location in agent[1]['route']:
                locations.append({'lat': location[0], 'lon': location[1]})
            agent[1]['route'] = locations

    current = result['events']['current_event']
    json_events = {'current_event': {}, 'pending_events': []}

    if current is not None:
        for event in current:
            if isinstance(current[event], str):
                continue
            if isinstance(current[event], list):
                json_events['current_event'][event] = []
                for obj_event in current[event]:
                    json_events['current_event'][event].append(obj_event.json())
            else:
                json_events['current_event'][event] = current[event].json()

    for idx, event_list in enumerate(result['events']['pending_events']):
        json_events['pending_events'].append([])
        for event in event_list:
            json_events['pending_events'][idx].append(event.json())

    result['events'] = json_events

    return jsonify(result)


@app.route('/finish', methods=['GET'])
def finish():
    if request.remote_addr != base_url:
        return jsonify(message='This endpoint can not be accessed.')

    import os
    os._exit(0)


if __name__ == '__main__':
    app.debug = False
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    CORS(app)
    if requests.get(f'http://{base_url}:{api_port}/start'):
        print('Simulation ')
        serve(app, host=base_url, port=port)
    else:
        print('Errors during startup')
