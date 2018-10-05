import _thread
import time
import jwt
import json

from src.communication.ActionResult import ActionResult
from src.__init__ import socketio
from src.communication.events.emiters import response_to_action_connect, response_to_action_deliver, \
    response_to_action_ready, emit_pre_step
from src.communication.events.prepare_action import verify_method
from src.communication.AgentManager import AgentManager

agent_manager = AgentManager()
valid_time = True
init = time.time()


@socketio.on('receive_jobs')
def handle_connection(message):

    agent = (message['id'], (message['method'], message['parameters'][0], message['parameters'][1]))
    method = agent[1][0]

    verified = verify_method(method, agent)
    from src.manager import SimulationInstance
    simulation_manager = SimulationInstance.get_instance('')
    response = simulation_manager.do_step([agent])
    response = ('received_jobs_result', verified)
    call_responses(response, 'receive_jobs','')



@socketio.on('connect')
def respond_to_request(message=None):
    global init, valid_time

    init = time.time()

    response = ('connection_result', {'success': True})

    call_responses(response, 'connect', '')

    if not valid_time:
        # socketio.
        pass


@socketio.on('ready')
def respond_to_request_ready(message):
    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)
    agent_manager.manage_agents(decoded)
    from src.manager import SimulationInstance
    simulation_manager = SimulationInstance.get_instance('')
    call_responses(simulation_manager.agents_list(), 'ready', message['data'])
    response = simulation_manager.do_pre_step()
    emit_pre_step(response, message['data'])


def call_responses(results, caller, token):
    if caller == 'ready':
        response_to_action_ready(json.dumps(results), token)

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
