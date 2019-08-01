"""This module is the entry point for all the calls that the simulation will receive, all the validations and controls
are done here. It represents the server of the simulation and also the step controller.

Note: any changes on the control functions must be done carefully."""

import os
import sys
import json
import time
import queue
import signal
import requests
import multiprocessing
from multiprocessing import Queue
from flask_socketio import SocketIO
from flask import Flask, request, jsonify
from communication.controllers.controller import Controller
from communication.helpers import json_formatter

base_url, api_port, simulation_port, step_time, first_step_time, method, secret, agents_amount, assets_amount = sys.argv[1:]


app = Flask(__name__)
socket = SocketIO(app=app)

controller = Controller(agents_amount, assets_amount, first_step_time, secret)
every_agent_registered = Queue()
one_agent_registered_queue = Queue()
actions_queue = Queue()


@app.route('/start_connections', methods=['POST'])
def start_connections():
    """Starts the API as entry point, before calling this functions the API will only answer that the simulation
    is not online.

    It also starts processes that will handle the first step cycle. The first step cycle can be completed in some
    different ways:

    1 - All the agents connected at once: This is the expected condition for the simulation to start running, after all
    the agents connect to it, the steps engine will proceed.

    2 - Less than the total of agents connected and the time ended: It is not the perfect scenario, but is possible. If
    just one of five agents connects to the simulation it will wait for the time to end, if it ends, the steps engine
    will proceed with only that agent connected.

    3 - No agent connected and the time ended: This is the worst scenario possible for the time, if no agent is connected
    than the simulation will never start.

    4 - The user pressed any button: This is the scenario where the user has the full control of the start, it will only
    start the steps engine when the user allows it.

    Note: This endpoint must be called from the simulation, it is not recommended to the user to call it on his own."""

    try:
        valid, message = controller.do_internal_verification(request)

        if not valid:
            return jsonify(message=f'This endpoint can not be accessed. {message}')

        if message['back'] != 1:
            controller.set_started()

            if method == 'time':
                multiprocessing.Process(target=first_step_time_controller, args=(every_agent_registered,), daemon=True).start()

            else:
                multiprocessing.Process(target=first_step_button_controller, daemon=True).start()

        else:
            multiprocessing.Process(target=first_step_time_controller, args=(one_agent_registered_queue,), daemon=True).start()

        controller.start_timer()

        return jsonify('')

    except json.JSONDecodeError:
        return jsonify(message='This endpoint can not be accessed.')


def first_step_time_controller(ready_queue):
    """Waits for either all the agents connect or the time end.

    If all the agents connect, it will start the steps engine and run the simulation with them.
    If some of the agents does not connect it will call the start_connections endpoint and retry."""

    agents_connected = False

    try:
        if int(agents_amount) > 0:
            agents_connected = ready_queue.get(block=True, timeout=int(first_step_time))

        else:
            agents_connected = True

    except queue.Empty:
        pass

    if not agents_connected:
        requests.post(f'http://{base_url}:{api_port}/start_connections', json={'secret': secret, 'back': 1})

    else:
        requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json={'secret': secret})

    os.kill(os.getpid(), signal.SIGTERM)


def first_step_button_controller():
    """Wait for the user to press any button, the recommended is 'Enter', but there are no restrictions."""

    sys.stdin = open(0)
    print('When you are ready press "Enter"')
    sys.stdin.read(1)

    requests.get(f'http://{base_url}:{api_port}/start_step_cycle', json=secret)


@app.route('/start_step_cycle', methods=['GET'])
def start_step_cycle():
    """Start the steps engine and notify the agents that are connected to it that the simulation is starting.

    Note: When this endpoint is called, the agents or social assets can only send actions to the simulation.
    Note: This endpoint must be called from the simulation, it is not recommended to the user to call it on his own."""

    valid, message = controller.do_internal_verification(request)

    if not valid:
        return jsonify(message=f'This endpoint can not be accessed. {message}')

    controller.finish_connection_timer()

    sim_response = requests.post(f'http://{base_url}:{simulation_port}/start', json={'secret': secret}).json()

    notify_actors('simulation_started', sim_response)

    multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

    return jsonify('')


@app.route('/connect_agent', methods=['POST'])
def connect_agent():
    """Connect the agent.

    If the agent is successfully connected, the simulation will return its token, any errors, it will return the error
    message and the corresponding status."""

    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_agent_connection(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@app.route('/connect_asset', methods=['POST'])
def connect_asset():
    """Connect the social asset.

    If the social asset is successfully connected, the simulation will return its token, any errors, it will return
    the error message and the corresponding status."""

    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_social_asset_connection(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@app.route('/register_agent', methods=['POST'])
def register_agent():
    """Register the agent.

    Note: The agent must be connected to register itself."""

    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_agent_registration(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@app.route('/register_asset', methods=['POST'])
def register_asset():
    """Register the social asset.

    Note: The social asset must be connected to register itself."""

    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_social_asset_registration(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    response['message'] = message

    return jsonify(response)


@socket.on('connect_registered_agent')
def connect_registered_agent(msg):
    """Connect the socket of the agent.

    If no errors found, the agent information is sent to the engine and it will create its own object of the agent.

    Note: The agent must be registered to connect the socket."""

    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_agent_socket_connection(request, msg)

    if status == 1:
        try:
            sim_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                         json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully connected.'

                if controller.agents_amount == len(controller.manager.agents_sockets_manager.get_tokens()):
                    every_agent_registered.put(True)

                one_agent_registered_queue.put(True)

            else:
                response['status'] = sim_response['status']
                response['message'] = sim_response['message']

        except requests.exceptions.ConnectionError:
            response['status'] = 6
            response['message'] = 'Simulation is not online.'

    else:
        response['status'] = status
        response['message'] = message

    return json.dumps(response, sort_keys=False)


@socket.on('connect_registered_asset')
def connect_registered_asset(msg):
    """Connect the socket of the social asset.

    If no errors found, the social asset information is sent to the engine and it will create its own object
    of the social asset. If the engine does not throw any errors, than the object created is returned.

    Note: The social asset must be registered to connect the socket."""

    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_social_asset_socket_connection(request, msg)

    if status == 1:
        try:
            sim_response = requests.post(f'http://{base_url}:{simulation_port}/register_asset',
                                         json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = sim_response['social_asset']
                one_agent_registered_queue.put(True)

            else:
                response['status'] = sim_response['status']
                response['message'] = sim_response['message']

        except requests.exceptions.ConnectionError:
            response['status'] = 6
            response['message'] = 'Simulation is not online.'

    else:
        response['status'] = status
        response['message'] = message

    return json.dumps(response, sort_keys=False)


@app.route('/finish_step', methods=['GET'])
def finish_step():
    """Finish each step of the simulation.

    Every time the simulation finished one step, all the actions sent are processes by the engine and
    the agents and social assets are notified if the simulation ended, their actions results or if the
    simulation restarted.
    Internal errors at the engine of the API will stop the system to prevent of running hundreds of steps
    to find that on step 12 the simulation had an error and all the next steps were not executed properly.

    Note: When the engine is processing the actions, the agents or social assets can not send any action.
    Note: This endpoint must be called from the simulation, it is not recommended to the user to call it on his own."""

    valid, message = controller.do_internal_verification(request)

    if not valid:
        return jsonify(message=f'This endpoint can not be accessed. {message}')

    try:
        controller.set_processing_actions()
        tokens_actions_list = [*controller.manager.get_actions('agent'), *controller.manager.get_actions('social_asset')]
        sim_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions', json={'actions': tokens_actions_list, 'secret': secret}).json()

        controller.manager.clear_workers()

        if sim_response['status'] == 0:
            print(sim_response['message'])
            print('An internal error occurred. Shutting down...')
            requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
            multiprocessing.Process(target=auto_destruction, daemon=True).start()

        if sim_response['message'] == 'Simulation finished.':
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/restart', json={'secret': secret}).json()

            if sim_response['status'] == 0:
                notify_actors('simulation_ended', {'status': 1, 'message': 'Simulation ended all matches.'})

                requests.get(f'http://{base_url}:{simulation_port}/terminate', json={'secret': secret, 'api': True})
                multiprocessing.Process(target=auto_destruction, daemon=True).start()

            else:
                notify_actors('simulation_started', sim_response)

                controller.set_processing_actions()
                multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

        else:
            notify_actors('action_results', sim_response)

            controller.set_processing_actions()
            multiprocessing.Process(target=step_controller, args=(actions_queue,), daemon=True).start()

    except requests.exceptions.ConnectionError:
        pass

    return jsonify(0)


def step_controller(ready_queue):
    """Wait for all the agents to send their actions or the time to end either one will cause the method to call
    finish_step."""

    try:
        if int(agents_amount) > 0:
            ready_queue.get(block=True, timeout=int(step_time))

    except queue.Empty:
        pass

    try:
        requests.get(f'http://{base_url}:{api_port}/finish_step', json={'secret': secret})
    except requests.exceptions.ConnectionError:
        pass

    os.kill(os.getpid(), signal.SIGTERM)


@app.route('/send_action', methods=['POST'])
def send_action():
    """Receive all the actions from the agents or social assets.

    Note: The actions are stored and only used when the step is finished and the simulation process it."""

    response = {'status': 1, 'result': True, 'message': 'Error.'}

    status, message = controller.do_action(request)

    if status != 1:
        response['status'] = status
        response['result'] = False

    else:
        every_socket = controller.manager.get_all('socket')
        tokens_connected_size = len([*every_socket[0], *every_socket[1]])
        agent_workers_size = len(controller.manager.get_workers('agent'))
        social_asset_workers_size = len(controller.manager.get_workers('social_asset'))

        if tokens_connected_size == agent_workers_size + social_asset_workers_size:
            actions_queue.put(True)

    response['message'] = message

    return jsonify(response)


@socket.on('disconnect_registered_agent')
def disconnect_registered_agent(msg):
    """Disconnect the agent.

    The agent is removed from the API and will not be able to connect of send actions to it."""

    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_agent_socket_disconnection(msg)

    if status == 1:
        try:
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/delete_agent',
                                        json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Agent successfully disconnected.'

            else:
                response['message'] = sim_response['message']

        except json.decoder.JSONDecodeError:
            response['message'] = 'An internal error occurred at the simulation.'

        except requests.exceptions.ConnectionError:
            response['message'] = 'Simulation is not online.'

    return json.dumps(response, sort_keys=False)


@socket.on('disconnect_registered_asset')
def disconnect_registered_asset(msg):
    """Disconnect the social asset.

    The social asset is removed from the API and will not be able to connect of send actions to it."""

    response = {'status': 0, 'result': False, 'message': 'Error.'}

    status, message = controller.do_social_asset_socket_disconnection(msg)

    if status == 1:
        try:
            sim_response = requests.put(f'http://{base_url}:{simulation_port}/delete_asset',
                                        json={'token': message, 'secret': secret}).json()

            if sim_response['status'] == 1:
                response['status'] = 1
                response['result'] = True
                response['message'] = 'Social asset successfully disconnected.'

            else:
                response['message'] = sim_response['message']

        except json.decoder.JSONDecodeError:
            response['message'] = 'An internal error occurred at the simulation.'

        except requests.exceptions.ConnectionError:
            response['message'] = 'Simulation is not online.'

    return json.dumps(response, sort_keys=False)


def notify_actors(event, response):
    """Notify the agents and social assets through sockets.

    Each agent and each social asset has its own message related.

    Note: If an unknown event name is given, the simulation will stop because it was almost certainly caused by
    internal errors."""

    tokens = [*controller.manager.agents_sockets_manager.get_tokens(), *controller.manager.assets_sockets_manager.get_tokens()]
    room_response_list = []
    for token in tokens:
        if event == 'simulation_started':
            info = json_formatter.simulation_started_format(response, token)

        elif event == 'simulation_ended':
            info = json_formatter.simulation_ended_format(response)

        elif event == 'action_results':
            info = json_formatter.action_results_format(response, token)

        else:
            exit('Wrong event name. Possible internal errors.')

        room = controller.manager.get(token, 'socket')
        room_response_list.append((room, json.dumps(info)))

    for room, response in room_response_list:
        socket.emit(event, response, room=room)


@app.route('/terminate', methods=['GET'])
def terminate():
    """Terminate the process that runs the API.

    Note: This endpoint must be called from the simulation, it is not recommended to the user to call it on his own."""

    valid, message = controller.do_internal_verification(request)

    if not valid:
        return jsonify(message='This endpoint can not be accessed.')

    if 'back' not in message:
        return jsonify(message='This endpoint can not be accessed.')

    if message['back'] == 0:
        multiprocessing.Process(target=auto_destruction, daemon=True).start()
    else:
        socket.stop()
        os.kill(os.getpid(), signal.SIGTERM)

    return jsonify('')


def auto_destruction():
    """Wait one second and then call the terminate endpoint."""

    time.sleep(1)
    try:
        requests.get(f'http://{base_url}:{api_port}/terminate', json={'secret': secret, 'back': 1})
    except requests.exceptions.ConnectionError:
        pass

    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False
    print(f'API: Serving on http://{base_url}:{api_port}')
    socket.run(app=app, host=base_url, port=api_port)
