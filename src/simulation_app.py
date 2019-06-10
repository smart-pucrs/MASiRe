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

config_path, events_path, base_url, port, api_port = sys.argv[1:]


def start_instance(config_sim_path, config_events_path):
    with open(config_sim_path, 'r') as simulation_config:
        json_config = json.loads(simulation_config.read())

    return Simulation(json_config, config_events_path)


app = Flask(__name__)
simulation = start_instance(config_path, events_path)
initial_percepts = simulation.start()


@app.route('/register_agent', methods=['POST'])
def register_agent():
    if request.remote_addr != base_url:
        return jsonify(message='This endpoint can not be accessed.')

    agent_info = request.get_json(force=True)
    agent = simulation.create_agent(agent_info['token'], agent_info['agent_info']).json()

    events = initial_percepts[1].copy()
    map_percepts = initial_percepts[0].copy()

    # for event in events:
    #     if event == 'flood' and events[event]:
    #         events[event] = events[event].json()
    #     else:
    #         aux = []
    #         for x in events[event]:
    #             aux.append(x.json())
    #         events[event] = aux

    return jsonify({'agent': agent, 'map_percepts': map_percepts})


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

    result['events'] = [event.json() for event in result['events']]
    result['step'] = simulation.step

    return jsonify(result)


@app.route('/restart', methods=['GET'])
def restart():
    global simulation
    simulation = start_instance(config_path)
    global initial_percepts
    initial_percepts = simulation.start()

    return jsonify(0)


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
    init_percepts = copy.deepcopy(initial_percepts[1])
    if requests.post(f'http://{base_url}:{api_port}/start', json=[event.json() for event in init_percepts]):
        print('Simulation ')
        serve(app, host=base_url, port=port)
    else:
        print('Errors during startup')
