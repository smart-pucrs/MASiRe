import json
import sys
from datetime import date

import socketio
import time
import requests
import os
import signal

from flask import Flask, render_template, jsonify
from socketio.exceptions import ConnectionError as SocketError
from monitor_engine.controllers.monitor_manager import MonitorManager
from monitor_engine.helpers.logger import Logger

arguments = sys.argv[1:]

# Events strings
initial_percepts_event = 'initial_percepts'
percepts_event = 'percepts'
end_event = 'end'
bye_event = 'bye'
error_event = 'error'
connect_monitor_event = 'connect_monitor'
disconnect_monitor_event = 'disconnect_monitor'

if len(arguments) == 3:
    replay, base_url, monitor_port = arguments
    replay_mode = True
else:
    base_url, monitor_port, api_port, record, config, secret = sys.argv[1:]
    replay_mode = False

app = Flask(__name__)
socket = socketio.Client()
manager = None


@socket.on('connect')
def connect():
    global manager

    socket.emit(connect_monitor_event, '')
    response = requests.get(f'http://{base_url}:{api_port}/simulation_info').json() 
    manager = MonitorManager(response)


@socket.on(initial_percepts_event)
def initial_percepts_handler(data):
    print(f'[{initial_percepts_event}] ## Received.')

    if data['status']:
        try:
            manager.create_new_match(data['map_percepts'])

        except Exception as e:
            Logger.error(f'Error to create a new Match: {str(e)}')

    else:
        Logger.error(f"Error in Initial percepts event: {data['message']}")


@socket.on(percepts_event)
def percepts_handler(data):
    print(f'[{percepts_event}] ##  Received.')

    if data['status']:
        try:
            manager.add_percepts(data['actors'], data['environment'])

        except Exception as e:
            Logger.error(f'Error to add new percepts: {str(e)}')

    else:
        Logger.error(f"Error in percepts event: {data['message']}")


@socket.on(end_event)
def end_handler(data):
    print(f'[{end_event}] ## Received.')

    if data['status']:
        try:
            manager.add_match_report(data['report'])

        except Exception as e:
            Logger.error(f'Error to add the report of the match: {str(e)}')

    else:
        Logger.error(f"Error in end event: {data['message']}")


@socket.on(bye_event)
def bye_handler(data):
    print(f'[{bye_event}] ## Received.')

    if data['status']:
        try:
            manager.add_simulation_report(data['report'])

            if record:
                record_simulation()
                Logger.normal('Match recorded.')

        except Exception as e:
            Logger.error(f'Error to add the simulation report: {str(e)}')

    else:
        Logger.error(f"Error in bye event: {data['message']}")


@socket.on(error_event)
def error_handler(data):
    print(f'[{error_event}] ## Received.')

    Logger.error(data['message'])


def record_simulation():
    current_date = date.today().strftime('%d-%m-%Y')
    hours = time.strftime("%H:%M:%S")
    file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

    abs_path = os.getcwd() + '/replays/' + file_name

    try:
        formatted_data = manager.format_simulation_data()

        with open(abs_path, 'w+') as file:
            file.write(json.dumps(formatted_data, sort_keys=False, indent=4))

        Logger.normal('Simulation recorded.')

    except Exception as e:
        Logger.error(f'Error to record the simulation: {str(e)}')


def load_simulation():
    global manager

    try:
        replay_path = os.getcwd() + '/replays/' + replay
        replay_data = json.loads(open(replay_path, 'r').read())

        manager = MonitorManager(replay_data['simulation_config'])
        manager.load_simulation(replay_data['matchs'], replay_data['sim_report'])

        Logger.normal('Simulation loaded.')

    except Exception as e:
        Logger.error(f'Error to load the simulation: {str(e)}')


@app.route('/')
def home():
    # return render_template('index.html')
    return 'Teste'

#
# @app.route('/next_step', methods=['GET'])
# def next_step():
#     data = {'status': False, 'message': ''}
#
#     try:
#         data['data'] = manager.next_step()
#         data['status'] = True
#
#     except Exception as e:
#         data['message'] = str(e)
#
#     return jsonify(data)
#
#
# @app.route('/next_match', methods=['GET'])
# def next_match():
#     data = {'status': False, 'message': ''}
#
#     try:
#         data['data'] = manager.next_match()
#         data['status'] = True
#
#     except Exception as e:
#         data['message'] = str(e)
#
#     return jsonify(data)
#
#
# @app.route('/prev_match', methods=['GET'])
# def prev_match():
#     data = {'status': False, 'message': ''}
#
#     try:
#         data['data'] = manager.prev_match()
#         data['status'] = True
#
#     except Exception as e:
#         data['message'] = str(e)
#
#     return jsonify(data)
#
#
# @app.route('/prev_step', methods=['GET'])
# def prev_step():
#     data = {'status': False, 'message': ''}
#
#     try:
#         data['data'] = manager.prev_step()
#         data['status'] = True
#
#     except Exception as e:
#         data['message'] = str(e)
#
#     return jsonify(data)
#
#
# @app.route('/init', methods=['GET'])
# def init_monitor():
#     data = {'status': False, 'message': ''}
#
#     try:
#         response = manager.get_initial_information()
#         data.update(response)
#         data['status'] = True
#
#     except Exception as e:
#         data['message'] = f'Unknown error: {str(e)}'
#
#     return jsonify(data)


if __name__ == "__main__":
    if replay_mode:
        try:
            print('replay')
            load_simulation()
        except Exception as e:
            print(str(e))

    else:
        while True:
            try:
                socket.connect(f'http://{base_url}:{api_port}')
                break

            except SocketError as error:
                Logger.error('Error to connect the monitor socket to API.')
                Logger.error('Try to connect again...')

                time.sleep(1)

        try:
            print('live')
        except Exception as e:
            print(str(e))

    app.run(host=base_url, port=int(monitor_port))
