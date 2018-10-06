import time
import jwt
import json

from src.communication.action_result import ActionResult
from src.__init__ import socketio
from src.communication.events.emiters import response_to_action_connect, response_to_action_deliver, \
    response_to_action_ready
from src.communication.events.prepare_action import handle_request
from src.communication.agent_manager import AgentManager

agent_manager = AgentManager()
init_general = None

agents = []


@socketio.on('receive_jobs')
def handle_connection(message):
    global init_general

    agent = json.loads(message)
    agent = (agent['id'], (agent['method'], agent['parameters'][0], agent['parameters'][1]))

    verified = handle_request(agent)

    response = ('received_jobs_result', verified)
    call_responses(response, 'receive_jobs')


@socketio.on('connect')
def respond_to_request(message=None):
    global init_general, agents

    if init_general is None:
        init_general = time.time()

    if time.time() - init_general < 30:
        response = ['connection_result', '']
        if len(agents) <= 5:
            response[1] = 'Success'
            response = (response[0], response[1])
            call_responses(response, 'connect')

        else:
            response[1] = 'Failure'
            response = (response[0], response[1])
            call_responses(response, 'connect')

    else:
        call_responses(['connection_result', 'Time is up! Sorry'], 'connect')


@socketio.on('ready')
def respond_to_request_ready(message):
    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)
    agent_manager.manage_agents(decoded)
    action_result = [ActionResult(message['data'], 'Let it be'), ActionResult(message['data'], 'Let it be2'),
                     ActionResult(message['data'], 'Let it be3')]
    call_responses(action_result, 'ready')


def call_responses(results, caller):
    if caller == 'ready':
        for result in results:
            response_to_action_ready(result.response, result.token)

    elif caller == 'connect':
        response_to_action_connect(results[0], results[1])

    elif caller == 'receive_jobs':
        response_to_action_deliver(results[0], results[1])
