import _thread
import time
import jwt
import json

from src.communication.ActionResult import ActionResult
from src.__init__ import socketio
from src.communication.events.emiters import response_to_action
from src.communication.events.prepare_action import verify_method
from src.communication.AgentManager import AgentManager
from flask_socketio import emit

agent_manager = AgentManager()
response = True
init = time.time()


@socketio.on('receive_jobs')
def handle_connection(message):
    agent = json.loads(message)

    agent = (agent['id'], (agent['method'], agent['parameters'][0], agent['parameters'][1]))
    method = agent[1][0]

    verified = verify_method(method, agent)
    emit('received_jobs_result', verified)


@socketio.on('connecting_agents')
def respond_to_request(message=None):
    global init

    init = time.time()
    _thread.start_new_thread(start_timer, (None,))
    # time.sleep(5)
    emit('connection_result', {'success': True})

    if not response:
        # socketio.
        pass


@socketio.on('ready')
def respond_to_request2(message):
    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)
    agent_manager.manage_agents(decoded)
    action_result = [ActionResult(message['data'], 'Let it be'), ActionResult(message['data'], 'Let it be2'),
                     ActionResult(message['data'], 'Let it be3')]
    call_responses(action_result)


def call_responses(results):
    for result in results:
        response_to_action(result.response, result.token)


def start_timer(input=None):
    global response

    while 1:
        if time.time() - init > 3:
            response = False
            break
