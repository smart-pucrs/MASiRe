import sys
import socketio
import time
import requests
import json
import os
import signal

from datetime import date
from flask import Flask, render_template, jsonify

arguments = sys.argv[1:]

if len(arguments) == 3:
    replay, base_url, monitor_port = arguments
    replay_mode = True
else:
    base_url, monitor_port, api_port, record, config, secret = sys.argv[1:]
    replay_mode = False

app = Flask(__name__)
socket = socketio.Client()

step = 0
current_match = 0
monitor_match = 0
simulation_info = {
    'simulation_info': None,
    'matchs': []
}


@socket.on('connect')
def connect():
    global simulation_info
    simulation_info['simulation_info'] = requests.get(f'http://{base_url}:{api_port}/simulation_info').json() 


@socket.on('monitor')
def monitor(data):
    # ------- STATUS -------
    # -1: ERROR
    #  0: SIMULATION FINISH
    #  1: SIMULATION RESTART
    #  2: STEP DATA
    # ----------------------
    global simulation_info, current_match

    if data['status'] == -1:
        print('[ MONITOR ][ ERROR ] ## A error occurrence, finishing the monitor.')
        os.kill(os.getpid(), signal.SIGTERM)

    elif data['status'] == 0:
        print('[ MONITOR ][ FINISH ] ## Finishing the monitor.')
        if record == 'True':
            write_replay()

    elif data['status'] == 1:
        current_match += 1

    else:
        simulation_info['matchs'][current_match]['steps_data'].append(data['sim_data'])
        

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/next_step', methods=['GET'])
def next_step():
    global step

    data = {'status': False, 'step_data': None, 'step': None, 'message': ''}

    try:
        data['step_data'] = simulation_info['matchs'][monitor_match]['steps_data'][step]
        total_steps = len(simulation_info['matchs'][monitor_match]['steps_data'])

        if step < total_steps - 1:
            step += 1

        else:
            data['message'] = 'There is no more steps.'            

        data['step'] = step
        data['total_steps'] = total_steps
        data['status'] = True

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/next_match', methods=['GET'])
def next_match():
    global step, monitor_match

    data = {'status': False, 'step_data': None, 'map': None, 'message': ''}

    try:
        if monitor_match == len(simulation_info['matchs']) - 1:
            data['message'] = 'There is no more matchs.'

            return jsonify(data)

        monitor_match += 1
        step = 0

        data['status'] = True
        total_steps = len(simulation_info['matchs'][monitor_match]['steps_data'])
        data['step_data'] = simulation_info['matchs'][monitor_match]['steps_data'][step]
        data['total_steps'] = total_steps
        data['map'] = simulation_info['matchs'][monitor_match]['map'] 

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/prev_match', methods=['GET'])
def prev_match():
    global step, monitor_match

    data = {'status': False, 'step_data': None, 'step': 0, 'message': ''}

    try:
        if monitor_match == 0:
            data['message'] = 'This match is already the first.'

            return jsonify(data)

        monitor_match -= 1
        step = 0

        data['step'] = step
        data['status'] = True
        total_steps = len(simulation_info['matchs'][monitor_match]['steps_data'])
        data['step_data'] = simulation_info['matchs'][monitor_match]['steps_data'][step]
        data['total_steps'] = total_steps
        data['map'] = simulation_info['matchs'][monitor_match]['map'] 

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)

@app.route('/prev_step', methods=['GET'])
def prev_step():
    global step

    data = {'status': False, 'step_data': None, 'step': None, 'total_steps': None, 'message': ''}

    try:
        data['step_data'] = simulation_info['matchs'][monitor_match]['steps_data'][step]
        total_steps = len(simulation_info['matchs'][monitor_match]['steps_data'])
        
        if step > 0:
            step -= 1
        else:
            data['message'] = 'Already in the first step.'

        data['step'] = step 
        data['total_steps'] = total_steps
        data['status'] = True

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/init', methods=['GET'])
def init_monitor():
    global simulation_info

    data = {'status': 0, 'simulation_info': None, 'total_matchs': 0, 'map': None, 'message': ''}

    try:
        data['status'] = 1
        data['simulation_info'] = simulation_info['simulation_info']
        data['total_matchs'] = len(simulation_info['matchs'])
        data['map'] = simulation_info['matchs'][monitor_match]['map']

    except Exception as e:
        print(f'[ MONITOR ][ ERROR ] ## Unknown error: {str(e)}')
        data['message'] = f'Unknown error: {str(e)}'

    return jsonify(data)


def write_replay():
    current_date = date.today().strftime('%d-%m-%Y')
    hours = time.strftime("%H:%M:%S")
    file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

    abs_path = os.getcwd() + '/replays/'

    with open(str(abs_path + file_name), 'w+') as file:
        file.write(json.dumps(simulation_info, sort_keys=False, indent=4))


def init_replay_mode():
    global simulation_info

    replay_path = os.getcwd() + '/replays/' + replay

    try:
        with open(replay_path, 'r') as file:
            simulation_info = json.loads(file.read())
    
    except Exception as e:
        print(f'[ MONITOR ][ ERROR ] ## Unknown error: {str(e)}')


def init_live_mode():
    try:
        config_location = os.getcwd() + '/' + config
        maps = json.load(open(config_location, 'r'))['map']['maps']

        for map_info in maps:
            simulation_info['matchs'].append({'map': map_info, 'steps_data': []})

    except Exception as e:
        print(f'[ MONITOR ][ ERROR ] ## Unknown error: {str(e)}')


if __name__ == "__main__":
    if replay_mode:
        init_replay_mode()

    else:
        time.sleep(.5)
        socket.connect(f'http://{base_url}:{api_port}')
        init_live_mode()

    app.run(host=base_url, port=int(monitor_port))
