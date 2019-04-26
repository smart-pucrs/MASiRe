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

    try:
        simulation_response = \
            requests.post(f'http://{base_url}:{simulation_port}/register_agent', json=token).json()

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

    if controller.simulation_response:
        return controller.simulation_response[token]
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

        jobs.append((token, (action_name, action_params)))

    try:
        controller.simulation_response = \
            requests.post(f'http://{base_url}:{simulation_port}/do_actions', json=jobs).json()

    except requests.exceptions.ConnectionError:
        print('Simulation is not online')

    multiprocessing.Process(target=counter, args=(step_time,)).start()
    return jsonify("")


def counter(sec):
    sec = int(sec)
    time.sleep(sec)
    try:
        requests.get(f'http://{base_url}:{port}/time_ended')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    controller = Controller()
    multiprocessing.Process(target=counter, args=(first_conn_time,)).start()
    serve(app, host=base_url, port=port)
