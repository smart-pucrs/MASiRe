import time
import jwt
import json

from src.__init__ import socketio
from src.communication.events.emiters import response_to_action_connect, response_to_action_deliver, \
    response_to_action_ready, emit_pre_step
from src.communication.agent_manager import AgentManager
from src.communication.events.prepare_action import handle_request
from src.manager import simulation_instance

agent_manager = AgentManager()
init_general = None

agents = []
count = 1


@socketio.on('receive_jobs')
def handle_connection(message):
    global count

    message = json.loads(message)
    agent = (message['id'], (message['method'], message['parameters'][0], message['parameters'][1]))
    method = agent[1][0]
    simulation_manager = simulation_instance.get_instance('')

    if handle_request(agent):
        agent = (count, (agent[1][0], agent[1][1], agent[1][2]))
        count += 1
        response = simulation_manager.do_step([agent])
        response = ('received_jobs_result', response)

        call_responses(response, 'receive_jobs', '')


@socketio.on('connect')
def respond_to_request(message=None):
    global init_general, agents

    init = time.time()

    response = ('connection_result', {'success': True})

    call_responses(response, 'connect', '')
    if init_general is None:
        init_general = time.time()

    if time.time() - init_general < 30:
        response = ['connection_result', '']
        if len(agents) <= 5:
            response[1] = 'Success'
            response = (response[0], response[1])
            call_responses(response, 'connect', '')

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
    from src.manager import simulation_instance
    simulation_manager = simulation_instance.get_instance('')
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
