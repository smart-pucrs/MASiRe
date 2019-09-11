import pathlib
import sys
import socketio
import time
import requests
import json
import os
import signal

from datetime import date
from flask import Flask, render_template, jsonify, send_file

base_url, monitor_port, api_port, path_replay, config, secret = sys.argv[1:]
app = Flask(__name__)
socket = socketio.Client()

step = 0
maps = None
has_next = True
current_match = 0
simulation_info = {}
simulation_steps = []


@socket.on('connect')
def connect():
    global simulation_info
    simulation_info = requests.get(f'http://{base_url}:{api_port}/simulation_info').json() 


@socket.on('monitor')
def monitor(data):
    # ------- STATUS -------
    # -1: ERROR
    #  0: SIMULATION FINISH
    #  1: SIMULATION RESTART
    #  2: STEP DATA
    # ----------------------
    global simulation_steps

    if data['status'] == -1:
        print('[ MONITOR ][ ERROR ] ## A error occurrence, finishing the monitor.')
        os.kill(os.getpid(), signal.SIGTERM)

    elif data['status'] == 0:
        print('[ MONITOR ][ FINISH ] ## Finishing the monitor.')
        if path_replay != 'None':
            write_replay(path_replay)

    elif data['status'] == 1:
        if path_replay != 'None':
            write_replay(path_replay)

        print('[ MONITOR ][ RESTART ] ## restart the monitor.')

    else:
        simulation_steps.append(data['sim_data'])
        

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/next', methods=['GET'])
def next():
    global step

    print(step)

    data = {'status': False, 'step_data': None, 'step': None, 'message': ''}

    try:
        print(step, len(simulation_steps))
        data['step_data'] = simulation_steps[step]
        
        if step < len(simulation_steps) - 1:
            step += 1
            print('STEP: ', step)

        else:
            data['message'] = 'There is no more steps.'            

        data['step'] = step
        data['total_steps'] = len(simulation_steps)
        data['status'] = True

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/prev', methods=['GET'])
def prev():
    global step

    data = {'status': False, 'step_data': None, 'step': None, 'total_steps': None, 'message': ''}

    try:
        data['step_data'] = simulation_steps[step]
        
        if step > 0:
            step -= 1
        else:
            data['message'] = 'Already in the first step.'

        data['step_data'] = simulation_steps[step]
        data['step'] = step 
        data['total_steps'] = len(simulation_steps)
        data['status'] = True

    except IndexError as e:
        data['message'] = str(e)

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/init', methods=['GET'])
def init_monitor():
    global maps, simulation_info

    try:
        config_location = os.getcwd() + '/' + config
        maps = json.load(open(config_location, 'r'))['map']['maps']

        first_map = maps.pop(0)
        del first_map['osm']

        simulation_info['map'] = first_map

    except Exception as e:
        print(f'[ MONITOR ][ ERROR ] ## Error when load the config file. Error: {str(e)}')

    return jsonify(simulation_info)


@app.route('/victim_icon', methods=['GET'])
def victim_icon():
    return send_file('templates/images/victim_icon.png')


@app.route('/flood_icon', methods=['GET'])
def flood_icon():
    return send_file('templates/images/flood_icon.png')


@app.route('/water_sample_icon', methods=['GET'])
def water_sample_icon():
    return send_file('templates/images/water_sample_icon.png')


@app.route('/photo_icon', methods=['GET'])
def photo_icon():
    return send_file('templates/images/photo_icon.png')


@app.route('/agent_icon', methods=['GET'])
def agent_icon():
    return send_file('templates/images/agent_icon.png')


def write_replay(path):
    json_steps = {}
    step_id = 0

    abs_path = os.getcwd() + '/' + path

    for json_step in simulation_steps:
        json_steps[step_id] = json_step
        step_id += 1
    
    current_date = date.today().strftime('%d-%m-%Y')
    hours = time.strftime("%H:%M:%S")

    file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

    with open(str(abs_path + '/' + file_name), 'w+') as file:
        file.write(json.dumps(json_steps, sort_keys=False, indent=4))


if __name__ == "__main__":
    time.sleep(.5)
    socket.connect(f'http://{base_url}:{api_port}')
    app.run(host=base_url, port=int(monitor_port))
