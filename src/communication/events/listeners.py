import _thread
import time
import jwt
import json

from src.communication.ActionResult import ActionResult
from src.__init__ import socketio
from src.communication.events.emiters import response_to_action_connect, response_to_action_deliver, \
    response_to_action_ready
from src.communication.events.prepare_action import verify_method
from src.communication.AgentManager import AgentManager

agent_manager = AgentManager()
valid_time = True
init = time.time()


@socketio.on('receive_jobs')
def handle_connection(message):
    agent = json.loads(message)

    agent = (agent['id'], (agent['method'], agent['parameters'][0], agent['parameters'][1]))
    method = agent[1][0]

    verified = verify_method(method, agent)
    response = ('received_jobs_result', verified)
    call_responses(response, 'receive_jobs')


@socketio.on('connect')
def respond_to_request(message=None):
    global init, valid_time

    init = time.time()
    _thread.start_new_thread(start_timer, (None,))
    response = ('connection_result', {'success': True})

    call_responses(response, 'connect')

    if not valid_time:
        # socketio.
        pass


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


def start_timer(input=None):
    global valid_time

    while 1:
        if time.time() - init > 3:
            valid_time = False
            break
