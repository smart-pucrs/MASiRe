import sys
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
manager = MonitorManager()


@socket.on('connect')
def connect():
    socket.emit(connect_monitor_event, '')
    response = requests.get(f'http://{base_url}:{api_port}/simulation_info').json() 
    manager.set_simulation_info(response)


@socket.on(initial_percepts_event)
def initial_percepts_handler(data):
    print(f'[{initial_percepts_event}] ## Received.')
    pass


@socket.on(percepts_event)
def percepts_handler(data):
    print(f'[{percepts_event}] ##  Received.')
    pass


@socket.on(end_event)
def end_handler(data):
    print(f'[{end_event}] ## Received.')
    pass


@socket.on(bye_event)
def bye_handler(data):
    print(f'[{bye_event}] ## Received.')
    pass


@socket.on(error_event)
def error_handler(data):
    print(f'[{error_event}] ## Received.')
    pass


@socket.on('monitor')
def monitor(data):
    # CODE -1 : ERROR
    if data['status'] == -1:
        Logger.error('A error occurrence, finishing the monitor.')

        os.kill(os.getpid(), signal.SIGTERM)

    # CODE 0 : SIMULATION FINISH
    elif data['status'] == 0:
        Logger.normal('Finishing the monitor.')

        if record:
            manager.save_replay()

    # CODE 1 : SIMULATION RESTART
    elif data['status'] == 1:
        Logger.normal('Simulation restarted.')
        manager.next_match_api()

    # CODE 2 : STEP DATA
    else:
        Logger.normal('Update data.')

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
            #manager.init_replay_mode(replay)
            print('replay')
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

                time.sleep(2)

        try:
            #manager.init_live_mode(config)
            print('live')
        except Exception as e:
            print(str(e))


    app.run(host=base_url, port=int(monitor_port))
