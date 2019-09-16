import sys
import socketio
import time
import requests
import os
import signal

from flask import Flask, render_template, jsonify
from socketio.exceptions import ConnectionError as SocketError
from monitor_engine.monitor_manager import MonitorManager

arguments = sys.argv[1:]

if len(arguments) == 3:
    replay, base_url, monitor_port = arguments
    replay_mode = True
else:
    base_url, monitor_port, api_port, record, config, secret = sys.argv[1:]
    replay_mode = False

app = Flask(__name__)
socket = socketio.Client()
manager = MonitorManager()


@socket.on('connect')
def connect():
    response = requests.get(f'http://{base_url}:{api_port}/simulation_info').json() 
    manager.set_simulation_info(response)


@socket.on('monitor')
def monitor(data):
    # CODE -1 : ERROR
    if data['status'] == -1:
        print('[ MONITOR ][ ERROR ] ## A error occurrence, finishing the monitor.')
        os.kill(os.getpid(), signal.SIGTERM)

    # CODE 0 : SIMULATION FINISH
    elif data['status'] == 0:
        print('[ MONITOR ][ FINISH ] ## Finishing the monitor.')
        if record:
            manager.save_replay()

    # CODE 1 : SIMULATION RESTART
    elif data['status'] == 1:
        manager.next_match_api()

    # CODE 2 : STEP DATA
    else:
        manager.add_step_data(data['sim_data'])
        

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next_step', methods=['GET'])
def next_step():
    data = {'status': False, 'message': ''}

    try:
        data['data'] = manager.next_step()
        data['status'] = True

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/next_match', methods=['GET'])
def next_match():
    data = {'status': False, 'message': ''}

    try:
        data['data'] = manager.next_match()
        data['status'] = True

    except Exception as e:
        data['message'] = str(e)
        
    return jsonify(data)


@app.route('/prev_match', methods=['GET'])
def prev_match():
    data = {'status': False, 'message': ''}

    try:
        data['data'] = manager.prev_match()
        data['status'] = True

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/prev_step', methods=['GET'])
def prev_step():
    data = {'status': False, 'message': ''}

    try:
        data['data'] = manager.prev_step()
        data['status'] = True

    except Exception as e:
        data['message'] = str(e)

    return jsonify(data)


@app.route('/init', methods=['GET'])
def init_monitor():
    data = {'status': False, 'message': ''}

    try:
        response = manager.get_initial_information()
        data.update(response)
        data['status'] = True

    except Exception as e:
        data['message'] = f'Unknown error: {str(e)}'

    return jsonify(data)


if __name__ == "__main__":
    if replay_mode:
        try:
            manager.init_replay_mode(replay)

        except Exception as e:
            print(str(e))

    else:
        while True:
            try:
                socket.connect(f'http://{base_url}:{api_port}')
                break

            except SocketError as error:
                print('[ MONITOR ][ ERROR ] ## Error to connect the monitor socket to API.')
                print('[ MONITOR ][ ERROR ] ## Try to connect again...')
                time.sleep(2)

        try:
            manager.init_live_mode(config)

        except Exception as e:
            print(str(e))


    app.run(host=base_url, port=int(monitor_port))
