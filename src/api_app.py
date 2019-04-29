import jwt
import requests
import time
import sys
import multiprocessing
from flask import Flask, request, jsonify
from flask_cors import CORS
from communication.controller import Controller
from communication.temporary_agent import Agent
from waitress import serve

base_url, port, simulation_port, step_time, first_conn_time = sys.argv[1:]

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
CORS(app)


@app.route('/connect_agent', methods=['POST'])
def get_agent_token():
    """Return the token generated"""
    agent_response = {'can_connect': False}
    agent_info = request.get_json(force=True)

    if controller.check_population():
        token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

        agent = Agent(token, agent_info)

        controller.agents[token] = agent

        agent_response['can_connect'] = True
        agent_response['data'] = token

    return jsonify(agent_response)


@app.route('/validate_agent', methods=['POST'])
def validate_agent_token():
    """Check if the token is registered and then register the new agent in the simulation."""
    token = request.get_json(force=True)
    agent_response = {'agent_connected': False}

    if token not in controller.agents:
        return jsonify({'response': agent_response, 'message': "Token not registered"})

    agent_info = jwt.decode(token, 'secret', algorithms='HS256')
    agent = {'token': token, 'agent_info': agent_info}

    try:
        simulation_response = \
            requests.post(f'http://{base_url}:{simulation_port}/register_agent', json=agent).json()

    except requests.exceptions.ConnectionError:
        agent_response['message'] = 'Simulation is not online'
        return jsonify(agent_response)

    if controller.check_agent(token):
        if controller.check_timer():
            controller.agents[token].connected = True
            agent_response['agent_connected'] = True
            agent_response['step_time'] = step_time
            agent_response['agent_info'] = simulation_response

    return jsonify(agent_response)


@app.route('/send_job', methods=['POST'])
def register_job():
    """Save the job ."""
    agent_response = {'job_delivered': False}

    try:
        message = request.get_json(force=True)
        token = message['token']

        if token not in controller.agents:
            return jsonify({'response': agent_response, 'message': "Token not registered"})

        action = message['action']
        params = [*message['parameters']]

        controller.agents[token].action = (action, params)
        controller.agents[token].action_name = action
        controller.agents[token].action_param = params
        agent_response['job_delivered'] = True

        return jsonify(agent_response)

    except TypeError as t:
        return jsonify({'response': agent_response, 'message': t})

    except KeyError as k:
        return jsonify({'response': agent_response, 'message': k})


@app.route('/get_job', methods=['POST'])
def get_job():
    """Return the agent state and job result."""
    token = request.get_json(force=True)
    if token not in controller.agents:
        return jsonify({'response': False, 'message': "Token not registered"})

    if isinstance(controller.simulation_response, str):
        return jsonify(controller.simulation_response)
    elif controller.simulation_response:
        for agent_token, agent_dict in controller.simulation_response["action_results"]:
            if token == agent_token:
                return jsonify(agent_dict)
    else:
        return jsonify({'response': False, 'message': "No data from simulation"})


@app.route('/time_ended', methods=['GET'])
def finish_step():
    """Send all the jobs to the simulation and save the results."""
    if request.remote_addr != base_url:
        return jsonify("Error")

    jobs = []

    for token in controller.agents:
        action_name = controller.agents[token].action_name
        action_params = controller.agents[token].action_param

        jobs.append({'token': token, 'action': action_name, 'parameters': action_params})

    try:
        controller.simulation_response = \
            requests.post(f'http://{base_url}:{simulation_port}/do_actions', json=jobs).json()

        if isinstance(controller.simulation_response, str):
            return jsonify(1)
        print("time ended")
    except requests.exceptions.ConnectionError:
        print('Simulation is not online')

    multiprocessing.Process(target=counter, args=(step_time,)).start()
    return jsonify("")


def counter(sec):
    sec = int(sec)
    time.sleep(sec)

    try:
        end_code = requests.get(f'http://{base_url}:{port}/time_ended').json()
        if isinstance(end_code, int):
            requests.get(f'http://{base_url}:{simulation_port}/finish')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    controller = Controller()
    multiprocessing.Process(target=counter, args=(first_conn_time,)).start()
    serve(app, host=base_url, port=port)
