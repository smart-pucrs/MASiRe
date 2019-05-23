import sys
import jwt
import time
import json
import requests
import queue
import multiprocessing
from multiprocessing import Queue
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from src.communication.temporary_agents import JobSenderAgent, ConnectedAgent
from src.communication.controller import Controller

base_url, port, simulation_port, step_time, first_conn_time, qtd_agents = sys.argv[1:]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
socket = SocketIO(app=app)
controller = Controller(qtd_agents, first_conn_time)
all_connected_queue = Queue()


@app.route('/connect_agent', methods=['POST'])
def get_agent_token():
    """Return the token generated"""
    if controller.terminated:
        return jsonify({'message': 'Simulation already finished'})

    agent_response = {'can_connect': False}
    agent_info = request.get_json(force=True)

    if controller.check_population():
        if controller.check_timer():
            if not controller.check_connected(agent_info):
                token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

                agent = ConnectedAgent(token, agent_info)

                controller.connected_agents[token] = agent

                agent_response['can_connect'] = True
                agent_response['data'] = token
            else:
                agent_response['message'] = 'Agent already connected.'
        else:
            agent_response['message'] = 'Time is up.'
    else:
        agent_response['message'] = 'All agents connected.'

    return jsonify(agent_response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent_token():
    """Check if the token is registered and then register the new agent in the simulation."""
    if controller.terminated:
        return jsonify({'message': 'Simulation already finished.'})

    token = request.get_json(force=True)
    agent_response = {'agent_connected': False}

    if controller.check_agent(token):
        try:
            agent = {'token': token, 'agent_info': controller.connected_agents[token].agent_info}
            simulation_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                                json=agent).json()

        except requests.exceptions.ConnectionError:
            agent_response['message'] = 'Simulation is not online.'
            return jsonify(agent_response)

        controller.connected_agents[token].connected = True
        agent_response['agent_connected'] = True
        agent_response['info'] = simulation_response
        agent_response['time'] = float(first_conn_time) - (time.time() - controller.first_timer)

    else:
        agent_response['message'] = 'Token not registered.'

    return jsonify(agent_response)


@app.route('/send_job', methods=['POST'])
def register_job():
    """Save the job ."""
    if controller.terminated:
        return jsonify({'message': 'Simulation already finished.'})

    if controller.check_agents_job():
        all_connected_queue.put(True)
        return jsonify({'message': 'The results will be sent.'})

    agent_response = {'job_delivered': False}

    if controller.check_timer():
        agent_response['message'] = 'Simulation still receiving connections.'
        return jsonify(agent_response)

    try:
        message = request.get_json(force=True)
        token = message['token']

        if not controller.check_agent(token):
            agent_response['message'] = 'Token not registered.'
            return jsonify(agent_response)

        if not controller.connected_agents[token].connected:
            agent_response['message'] = 'Agent not connected.'
            return jsonify(agent_response)

        if controller.agent_job[token].action_name:
            agent_response['message'] = 'The agent has already sent a job'
            return jsonify(agent_response)

        controller.agent_job[token] = JobSenderAgent()

        action = message['action']
        params = [*message['parameters']]

        controller.agent_job[token].action_name = action
        controller.agent_job[token].action_param = params

        agent_response['job_delivered'] = True
        agent_response['time'] = float(step_time) - (time.time() - controller.step_time) + 2

        return jsonify(agent_response)

    except TypeError as t:
        agent_response['message'] = t
        return jsonify(agent_response)

    except KeyError as k:
        agent_response['message'] = k
        return jsonify(agent_response)


@app.route('/start', methods=['GET'])
def _start():
    multiprocessing.Process(target=counter, args=(first_conn_time,), daemon=True).start()
    controller.first_timer = time.time()
    return jsonify('')


@app.route('/finish_step', methods=['GET'])
def finish_step():
    """Send all the jobs to the simulation and save the results."""

    if request.remote_addr != base_url:
        return jsonify('This endpoint can not be accessed.')

    if controller.step_time is None:
        controller.step_time = time.time()
        multiprocessing.Process(target=counter, args=(step_time,), daemon=True).start()
        return jsonify(0)

    controller.step_time = time.time()
    jobs = []

    for token in controller.agent_job:
        action_name = controller.agent_job[token].action_name
        action_params = controller.agent_job[token].action_param

        if action_name:
            jobs.append({'token': token, 'action': action_name, 'parameters': action_params})

        controller.reset_agent_job()

    try:
        simulation_response = requests.post(f'http://{base_url}:{simulation_port}/do_actions', json=jobs).json()

        if isinstance(controller.simulation_response, str):
            controller.terminated = True

            event = f'simulation_ended'
            response = json.dumps({'message': 'Simulation finished.'})
            socket.emit(event, response, broadcast=True)

            return jsonify(1)

        else:
            for token, agent, message in simulation_response['action_results']:
                event = f'job_result_{token}'
                response = json.dumps({'agent': agent, 'message': message, 'events': simulation_response['events']})
                socket.emit(event, response)

    except requests.exceptions.ConnectionError:
        print('Simulation is not online')

    multiprocessing.Process(target=counter, args=(step_time,), daemon=True).start()
    return jsonify(0)


def counter(sec):
    try:
        all_connected_queue.get(block=True, timeout=int(sec))
    except queue.Empty:
        pass
    print('Ended step')
    try:
        end_code = requests.get(f'http://{base_url}:{port}/finish_step').json()
        if end_code == 1:
            try:
                requests.get(f'http://{base_url}:{simulation_port}/finish')
            except requests.exceptions.ConnectionError:
                print('Simulation terminated.')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    socket.run(app=app, host='127.0.0.1', port='12345')
