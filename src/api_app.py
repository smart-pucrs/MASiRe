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

base_url, port, simulation_port, step_time, first_conn_time, qtd_agents = sys.argv[1:]

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
        if controller.check_timer():
            if not controller.check_connected(agent_info):
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

    if controller.check_agent(token):
        try:
            agent = {'token': token, 'agent_info': controller.agents[token].agent_info}
            simulation_response = requests.post(f'http://{base_url}:{simulation_port}/register_agent',
                                                json=agent).json()

        except requests.exceptions.ConnectionError:
            agent_response['message'] = 'Simulation is not online'
            return jsonify(agent_response)

        controller.agents[token].connected = True
        agent_response['agent_connected'] = True
        agent_response['step_time'] = int(step_time)
        agent_response['info'] = simulation_response

    else:
        agent_response['message'] = 'Token not registered'

    return jsonify(agent_response)


@app.route('/send_job', methods=['POST'])
def register_job():
    """Save the job ."""
    agent_response = {'job_delivered': False}

    try:
        message = request.get_json(force=True)
        token = message['token']

        if token not in controller.agents:
            agent_response['message'] = 'Token not registered'
            return jsonify(agent_response)

        if controller.agents[token].action_name:
            return jsonify({'response': agent_response, 'message': "The agent has already sent a job"})

        action = message['action']
        params = [*message['parameters']]

        controller.agents[token].action_name = action
        controller.agents[token].action_param = params
        agent_response['job_delivered'] = True

        return jsonify(agent_response)

    except TypeError as t:
        agent_response['message'] = t
        return jsonify(agent_response)

    except KeyError as k:
        agent_response['message'] = k
        return jsonify(agent_response)


@app.route('/get_job', methods=['POST'])
def get_job():
    """Return the agent state and job result."""
    token = request.get_json(force=True)
    if token not in controller.agents:
        return jsonify({'response': False, 'message': "Token not registered"})

    if isinstance(controller.simulation_response, str):
        return jsonify(controller.simulation_response)

    elif controller.simulation_response:
        if controller.simulation_response['action_results']:
            for agent_token, agent_dict in controller.simulation_response["action_results"]:
                if token == agent_token:
                    simulation_state = controller.simulation_response.copy()
                    simulation_state['action_results'] = agent_dict

                    return jsonify({'simulation_state': simulation_state})

        return jsonify({'response': False, 'message': "No action of agent from the last step"})

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

        if action_name:
            jobs.append({'token': token, 'action': action_name, 'parameters': action_params})

        controller.agents[token].action = ()
        controller.agents[token].action_name = ""
        controller.agents[token].action_param = []

    try:
        controller.simulation_response = \
            requests.post(f'http://{base_url}:{simulation_port}/do_actions', json=jobs).json()

        if isinstance(controller.simulation_response, str):
            return jsonify(1)

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
    multiprocessing.Process(target=counter, args=(first_conn_time,)).start()
    controller = Controller(qtd_agents, first_conn_time)
    serve(app, host=base_url, port=port)
