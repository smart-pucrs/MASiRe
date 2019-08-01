"""This module is the endpoint for the engine to communicate with the API. It is not supposed to receive external calls
of for the user to callit on its own. If is intended to call this module directly, be cautious."""

import os
import sys
import time
import signal
import logging
import requests
import multiprocessing
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS
from werkzeug.serving import run_simple
from simulation_engine.json_formatter import JsonFormatter

config_path, base_url, simulation_port, api_port, log, secret = sys.argv[1:]


app = Flask(__name__)
formatter = JsonFormatter(config_path)


@app.route('/start', methods=['POST'])
def start():
    """Start the engine."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.start())


@app.route('/register_agent', methods=['POST'])
def register_agent():
    """Register an agent in the engine."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.connect_agent(message['token']))


@app.route('/register_asset', methods=['POST'])
def register_asset():
    """Register a social asset in the engine."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.connect_social_asset(message['token']))


@app.route('/delete_agent', methods=['PUT'])
def delete_agent():
    """Delete a registered agent from the engine."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.disconnect_agent(message['token']))


@app.route('/delete_asset', methods=['PUT'])
def delete_asset():
    """Delete a registered social asset from the engine."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.disconnect_social_asset(message['token']))


@app.route('/do_actions', methods=['POST'])
def do_actions():
    """Process all the actions from the agents and social assets."""

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    return jsonify(formatter.do_step(message['actions']))


@app.route('/restart', methods=['PUT'])
def restart():
    """Restart the engine and save the log from the previous one."""

    global formatter

    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    can_restart = formatter.log()

    if can_restart['status'] == 1:
        response = formatter.restart()
    else:
        response = can_restart

    return jsonify(response)


@app.route('/terminate', methods=['GET'])
def finish():
    """Terminate the process the runs the engine."""

    global app
    message = request.get_json(force=True)

    if 'secret' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if secret != message['secret']:
        return jsonify(message='This endpoint can not be accessed.')

    if 'api' in message and message['api']:
        if log.lower() == 'true':
            formatter.save_logs()
        multiprocessing.Process(target=auto_destruction, daemon=True).start()

    elif 'api' in message and not message['api']:
        request.environ.get('werkzeug.server.shutdown')()

    return jsonify('')


def auto_destruction():
    """Wait for one second and then call the terminate endpoint."""

    time.sleep(1)
    try:
        requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': False})
    except requests.exceptions.ConnectionError:
        pass

    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    stacktrace = logging.getLogger('werkzeug')
    stacktrace.disabled = True

    app.debug = False
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False

    CORS(app)
    print('Simulation', end=': ')
    try:
        if requests.post(f'http://{base_url}:{api_port}/start_connections', json={'secret': secret, 'back': 0}):
            print(f'Serving on http://{base_url}:{simulation_port}')
            run_simple(application=app, hostname=base_url, port=int(simulation_port), use_reloader=False, use_debugger=False)
        else:
            print('Errors occurred during startup.')
    except requests.exceptions.ConnectionError:
        print('API is not online.')
