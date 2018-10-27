import time
import jwt
import json

from src.__init__ import socketio
from src.communication.events.emiters import response_to_action_connect, response_to_action_deliver, \
    response_to_action_ready
from src.communication.agent_manager import AgentManager
from src.communication.events.prepare_action import handle_request
from src.manager import simulation_instance
from src.communication.events.controller import Controller

agent_manager = AgentManager()
init_general = None
simulation_manager = None

agents = []
jobs = []
count = 1
aux = True
controller = Controller()


@socketio.on('receive_jobs')
def handle_connection(message):
    global count, jobs

    response = ['received_jobs_result', {'job_delivered': True}]

    message = json.loads(message)
    agent = (message['id'], (message['method'], message['parameters'][0], message['parameters'][1]))

    if handle_request(agent):
        jobs.append((count, (agent[1][0], agent[1][1], agent[1][2])))
        count += 1
        call_responses(response, 'receive_jobs')


@socketio.on('connect')
def respond_to_request(*message):
    global init_general, agents, aux

    response = ['connection_result', {'agent_connected': True}]

    if controller.check_timer():
        if controller.check_population():
            response[1]['agent_connected'] = False

        else:
            if aux:
                controller.agents.append('')
                aux = False

            else:
                aux = True

    else:
        simulation_manager.do_step(jobs)
        response[1]['agent_connected'] = False

    call_responses(response, 'connect')


@socketio.on('ready')
def respond_to_request_ready(message):
    global simulation_manager

    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)

    agent_manager.manage_agents(decoded)

    simulation_manager = simulation_instance.get_instance('')
    call_responses(simulation_manager.agents_list(), 'ready', message['data'])
    response = simulation_manager.do_pre_step()
    call_responses(response, message['data'])


def call_responses(results, caller, *token):
    if caller == 'ready':
        response_to_action_ready(json.dumps(results), token)

    elif caller == 'connect':
        response_to_action_connect(results[0], results[1])

    elif caller == 'receive_jobs':
        response_to_action_deliver(results[0], results[1])
