import jwt
import json
import requests
import time
import multiprocessing
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.communication.controller import Controller
from src.communication.temporary_agent import Agent


app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
CORS(app)


@app.route('/connect_agent', methods=['POST'])
def respond_to_request_ready():
    """
        Receive the agent information encoded and decode it
        Add the decoded agent to a list inside the agent_manager
        Use the singleton to get the simulation instance and prevent from instantiating the class multiple times
        Call two responses:
            First containing the agents_list
            Second containing the simulation pre step
    """
    agent_response = {'can_connect': False}
    agent_info = request.get_json(force=True)

    if controller.check_population():
        token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')

        agent = Agent(token, agent_info['url'])

        controller.agents[token] = agent

        agent_response['can_connect'] = True
        agent_response['data'] = token

    try:
        return jsonify(agent_response)
    except requests.exceptions.ConnectionError:
        message = 'Agent is not online'
        print(message)
        return jsonify(message)


@app.route('/validate_agent', methods=['POST'])
def respond_to_request():
    """"
        Handle all the connections

        Instantiate the response considering that the result will be True
        Verify if the passed time get over the expected time
        Verify if the number of agents connected get over the expected limit
        If passes the time limit
            If passes the agents limit
                Add agent to the agents list and do a trick due to the implementation of flask
                The trick is that the method will not add the same agent twice because the method is called
                 twice by the flask module
            Else
                Reponse receive False

        Send to the agents the response from the method
        """
    token = request.get_json(force=True)
    try:
        simulation_response = requests.post('http://localhost:8910/register_agent', json=token).json()
    except requests.exceptions.ConnectionError:
        message = 'Simulation is not online'
        print(message)
        return jsonify(message)

    agent_response = {'agent_connected': False}
    if controller.check_agent(token):
        if controller.check_timer():
            controller.agents[token].connected = True
            agent_response['agent_connected'] = True
            agent_response['agent_info'] = simulation_response

    try:
        return jsonify(agent_response)
    except requests.exceptions.ConnectionError:
        message = 'Agent is not online'
        print(message)
        return jsonify(message)


@app.route('/job', methods=['POST'])
def handle_connection():
    """
    Receive all the jobs from the agents

    Instantiate the response considering that the result will be True
    Collect the JSON message and fit it on the agent variable
    If the handle_connection returns True
    Add the job to the jobs done list
    Emit response to the agent

    Else
    Emit response containing False to the agent
    """
    agent_response = {'job_received': False}

    message = json.loads(request.get_json(force=True))
    token = message['token']
    action = message['action']

    params = [*message['parameters']]
    controller.agents[token].action = (action, params)
    agent_response['job_delivered'] = True

    try:
        return requests.post(controller.agents[token].url, json=agent_response).text
    except requests.exceptions.ConnectionError:
        message = 'Simulation is not online'
        print(message)
        return jsonify(message)


@app.route('/time_ended', methods=['GET'])
def finish_step():

    if request.remote_addr != '127.0.0.1':
        return jsonify(message='This endpoint can not be accessed.')

    jobs = []

    for token in controller.agents:
        action_name = controller.agents[token].action[0]

        action_params = []
        for param in controller.agents[token].action[1]:
            action_params.append(param)

        jobs.append((token, (action_name, action_params)))

    actions = json.dumps(jobs)
    try:
        simulation_response = requests.post('http://localhost:8910/do_actions', json=actions).json()
    except requests.exceptions.ConnectionError:
        message = 'Simulation is not online'
        print(message)
        return jsonify(message)

    for token in simulation_response:
        requests.get(controller.agents[token].url, json=simulation_response[token])

    multiprocessing.Process(target=counter, args=(10,)).start()


def counter(*args):
    time.sleep(args[0])
    requests.get('http://localhost:12345/time_ended')


if __name__ == '__main__':
    controller = Controller()
    multiprocessing.Process(target=counter, args=(3600,)).start()
    app.run(port=12345)
