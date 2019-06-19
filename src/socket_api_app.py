import sys
import jwt
import time
import json
import queue
import requests
import multiprocessing
from multiprocessing import Queue
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from communication.temporary_agents import ActionSenderAgent, ConnectedAgent
from communication.controller import Controller

base_url, port, simulation_port, step_time, first_conn_time, matches, qtd_agents, delay = sys.argv[1:]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
socket = SocketIO(app=app)
controller = Controller(qtd_agents, first_conn_time, matches, delay)

action_queue = Queue()
socket_clients = {}

send_action_result_event = 'send_action_result'
action_result_event = 'action_result'
simulation_result_event = 'simulation_result'


@socket.on('connect')
def connect():
    print("connect")
    # identifier = request.headers['name']
    # socket_clients[identifier] = request.sid


@socket.on('disconnect')
def disconnect():
    print('disconnect')
    # identifier = request.headers['name']
    # del socket_clients[identifier]


@socket.on('register')
def handle_message(message):
    identifier = json.loads(message)['name']
    socket_clients[identifier] = request.sid


@app.route('/connect_agent', methods=['POST'])
def connect_agent():
    """Return the token generated"""
    agent_response = {'status': False, 'message': ''}

    if not controller.started:
        agent_response['message'] = 'Simulation was not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished'

    else:
        agent_info = request.get_json(force=True)
        
        if controller.check_population():
            if controller.check_timer():
                if not controller.check_connected(agent_info):
                    token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

                    agent = ConnectedAgent(token, agent_info)

                    controller.connected_agents[token] = agent

                    agent_response['status'] = True
                    agent_response['data'] = token
                else:
                    agent_response['message'] = 'Agent already connected.'
            else:
                agent_response['message'] = 'Time is up.'
        else:
            agent_response['message'] = 'All agents connected.'

    return jsonify(agent_response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent():
    """Check if the token is registered and then register the new agent in the simulation."""
    agent_response = {'status': False, 'message': ''}

    if not controller.started:
        agent_response['message'] = 'Simulation was not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished.'

    else:
        token = request.get_json(force=True)
        
        if controller.check_agent(token):
            try:
                agent = {'token': token, 'agent_info': controller.connected_agents[token].agent_info}
                simulation_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                                    json=agent).json()

            except requests.exceptions.ConnectionError:
                agent_response['message'] = 'Simulation is not online.'
                return jsonify(agent_response)

            controller.connected_agents[token].connected = True
            controller.connected_agents[token].agent_constants = simulation_response['agent_constants']
            controller.connected_agents[token].agent_variables = simulation_response['agent_variables']

            agent_response['status'] = True
            agent_response['type'] = 'initial_percepts'
            agent_response['map_percepts'] = simulation_response['map_percepts']
            agent_response['agent_percepts'] = simulation_response['agent_constants']
            agent_response['time'] = float(first_conn_time) - (time.time() - controller.first_timer) + 1
        else:
            agent_response['message'] = 'Token not registered.'

    return jsonify(agent_response)


@socket.on('send_action')
def register_action(message):
    """Save the action ."""
    agent_response = {'status': False, 'message': ''}
    message = json.loads(message)

    if 'token' not in message:
        return

    identifier = controller.connected_agents[message['token']].agent_info['name']
    room = socket_clients[identifier]

    if not controller.started:
        agent_response['message'] = 'Simulation was not started.'

    elif controller.terminated:
        agent_response['message'] = 'Simulation already finished.'

    elif controller.check_timer():
        agent_response['message'] = 'Simulation still receiving connections.'

    else:
        try:
            token = message['token']

            if not controller.check_agent(token):
                agent_response['message'] = 'Token not registered.'

            elif not controller.connected_agents[token].connected:
                agent_response['message'] = 'Agent not connected.'

            else:
                if token not in controller.agent_action:
                    controller.agent_action[token] = ActionSenderAgent()

                    action = message['action']
                    params = [*message['parameters']]

                    controller.agent_action[token].action_name = action
                    controller.agent_action[token].action_param = params

                    agent_response['status'] = True

                    if controller.check_agents_action():
                        action_queue.put(True)

                elif controller.agent_action[token].action_name:
                    agent_response['message'] = 'The agent has already sent a action'

        except TypeError as t:
            agent_response['message'] = 'TypeError: ' + str(t)

        except KeyError as k:
            agent_response['message'] = 'KeyError: ' + str(k)

    socket.emit(send_action_result_event, agent_response, room=room)


@app.route('/start', methods=['POST'])
def _start():
    initial_percepts = request.get_json(force=True)

    controller.started = True
    controller.initial_percepts = initial_percepts
    multiprocessing.Process(target=counter, args=(first_conn_time, action_queue), daemon=True).start()
    controller.first_timer = time.time()
    return jsonify('')


@app.route('/finish_step', methods=['GET'])
def finish_step():
    """Send all the actions to the simulation and save the agent_responses."""
    if request.remote_addr != base_url:
        return jsonify('This endpoint can not be accessed.')

    if controller.step_time is None:
        initial_percepts = {'type': 'percepts', 'environment': {'events': json.loads(json.dumps(controller.initial_percepts, sort_keys=True)), 'step': 0}}

        for token in controller.connected_agents:
            initial_percepts['agent'] = controller.connected_agents[token].agent_variables

            identifier = controller.connected_agents[token].agent_info['name']
            room = socket_clients[identifier]
            socket.emit(action_result_event, json.dumps(initial_percepts), room=room)

        controller.step_time = True
        multiprocessing.Process(target=counter, args=(step_time, action_queue), daemon=True).start()

        return jsonify(0)

    actions = []
    idle_agents = controller.dif()

    try:
        for token in controller.agent_action:
            action_name = controller.agent_action[token].action_name
            action_params = controller.agent_action[token].action_param

            if action_name:
                actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        controller.reset_agent_action()
    except RuntimeError as r:
        if str(r) == 'dictionary changed size during iteration':
            time.sleep(2)
            actions = []
            for token in controller.agent_action:
                action_name = controller.agent_action[token].action_name
                action_params = controller.agent_action[token].action_param

                if action_name:
                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})
        else:
            raise r

    try:
        simulation_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions', json=actions).json()

        if isinstance(simulation_response, str):
            return jsonify(1)

        else:
            for item in simulation_response['action_results']:
                info = {'type': 'percepts', 'environment': {'events': simulation_response['events'],
                        'step': simulation_response['step']}}

                token = item[0]
                agent = item[1]

                info['agent'] = agent

                if len(item) > 2:
                    message = item[2]
                    info['message'] = message

                controller.connected_agents[token].agent_variables = agent
                identifier = controller.connected_agents[token].agent_info['name']
                room = socket_clients[identifier]
                socket.emit(action_result_event, json.dumps(info), room=room)

            info = {'type': 'percepts', 'environment': {'events': simulation_response['events'],
                    'step': simulation_response['step']}, 'message': 'agent don\'t send a action'}

            for token in idle_agents:
                agent = controller.connected_agents[token].agent_variables
                agent['last_action_result'] = False
                agent['last_action'] = 'pass'
                info['agent'] = agent

                identifier = controller.connected_agents[token].agent_info['name']
                room = socket_clients[identifier]
                socket.emit(action_result_event, json.dumps(info), room=room)

    except requests.exceptions.ConnectionError:
        print('Simulation is not online')

    multiprocessing.Process(target=counter, args=(step_time, action_queue), daemon=True).start()
    return jsonify(0)


@app.route('/restart', methods=['POST'])
def restart():
    response = request.get_json(force=True)

    for token in controller.connected_agents:
        controller.connected_agents[token].agent_variables = response['agents'][token]
        response = json.dumps(
            {'message': f'The match {controller.current_match} ended.',
             'match_result': response['match_result'][token], 'type': 'end'})

        identifier = controller.connected_agents[token].agent_info['name']
        room = socket_clients[identifier]
        socket.emit(simulation_result_event, response, room=room)

    controller.start_new_match()
    multiprocessing.Process(target=counter, args=(controller.delay, action_queue), daemon=True).start()
    return jsonify(0)


@app.route('/simulation_ended', methods=['POST'])
def notify_agents():
    controller.terminated = True
    simulation_report = request.get_json(force=True)

    for token in controller.connected_agents:
        identifier = controller.connected_agents[token].agent_info['name']
        room = socket_clients[identifier]

        match_result = json.dumps(
            {'message': f'The match {controller.current_match} ended.',
             'match_result': simulation_report['match'][token], 'type': 'end'})

        simulation_result = json.dumps(
            {'message': 'Simulation finished.',
             'simulation_report': simulation_report['report'][token], 'type': 'bye'})

        socket.emit(simulation_result_event, match_result, room=room)
        socket.emit(simulation_result_event, simulation_result, room=room)

    return jsonify(0)


def counter(sec, ready_queue):
    try:
        ready_queue.get(block=True, timeout=int(sec))
    except queue.Empty:
        pass
    try:
        code = requests.get(f'http://{base_url}:{port}/finish_step').json()
        if code == 1:
            if controller.check_matches():
                response = requests.get(f'http://{base_url}:{simulation_port}/simulation_report').json()
                try:
                    requests.get(f'http://{base_url}:{simulation_port}/finish')
                except requests.exceptions.ConnectionError:
                    requests.post(f'http://{base_url}:{port}/simulation_ended', json=response)
                    pass
            else:
                try:
                    response = requests.get(f'http://{base_url}:{simulation_port}/restart').json()
                    requests.post(f'http://{base_url}:{port}/restart', json=response)
                except requests.exceptions.ConnectionError:
                    pass
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print(f'API Serving on http://{base_url}:{port}')
    socket.run(app=app, host=base_url, port=port)
