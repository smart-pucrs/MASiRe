import jwt
import json
import requests
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_socketio import emit
from src.communication.controller import Controller
from src.communication.temporary_agent import Agent


app = Flask(__name__)
socketio = SocketIO(app)
app.debug = False
CORS(app)
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'


@socketio.on('first_message')
def respond_to_request_ready(message):
    """
        Receive the agent information encoded and decode it
        Add the decoded agent to a list inside the agent_manager
        Use the singleton to get the simulation instance and prevent from instantiating the class multiple times
        Call two responses:
            First containing the agents_list
            Second containing the simulation pre step
    """

    agent_response = {'can_connect': False}

    agent_info = json.loads(message)

    if controller.check_population():
        token = jwt.encode(agent_info, 'secret', algorithm='HS256').decode('utf-8')
        agent = Agent(token, len(controller.agents), None)
        controller.agents.append({token: agent})

        agent_response['can_connect'] = True
        agent_response['data'] = token
        event = f'received/{str(token)}'

    else:
        event = f'received/{agent_info.name}'

    emit(event, agent_response)


@socketio.on('connect_agent')
def respond_to_request(message=''):
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

        :param message: the JSON agent
        """
    token = json.loads(message)
    simulation_response = requests.post('http://localhost:5000/register_agent', json=token).json()

    agent_response = {'agent_connected': False}

    if controller.check_agent(token):
        if controller.check_timer():
            controller.agents[token].connected = simulation_response.is_active
            agent_response['agent_connected'] = simulation_response.is_active
            agent_response['agent_info'] = simulation_response

    requests.get('http://localhost:5678/start')
    emit(f'connection_result/{token}', json.dumps(agent_response))


@socketio.on('receive_jobs')
def handle_connection(message):
    """
    Receive all the jobs from the agents

    Instantiate the response considering that the result will be True
    Collect the JSON message and fit it on the agent variable
    If the handle_connection returns True
    Add the job to the jobs done list
    Emit response to the agent

    Else
    Emit response containing False to the agents

    :param message: the JSON agent
    """
    agent_response = {'job_received': False}

    message = json.loads(message)
    token = message['token']
    action = message['action']

    if action == 'move':
        location = (message['lat'], message['lon'])
        controller.agents[token].action = (action, location)
        agent_response['job_delivered'] = True

    emit(f'job_received/{token}', json.dumps(agent_response))


@app.route('time_ended', methods=['POST', 'GET'])
def finish_step():
    jobs = []

    for token in controller.agents:
        internal_id = controller.agents[token]
        action_name = controller.agents[token].action[0]

        action_params = []
        for param in controller.agents[token].action[1]:
            action_params.append(param)

        jobs.append((internal_id, (action_name, action_params)))

    actions = json.dumps(jobs)
    simulation_response = requests.post('http://localhost/5000', json=actions)

    emit('job_done', simulation_response)
    requests.get('http://localhost:5678/start')


controller = Controller()
socketio.run(app, port=12345, debug=True)
