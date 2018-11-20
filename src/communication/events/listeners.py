import jwt
import json

from src.__init__ import socketio
from src.communication.events.emiters import on_response
from src.communication.events.controller import Controller


controller = Controller()


@socketio.on('first_message')
def respond_to_request_ready(message):
    response = ['ready', [{'can_connect': False}, {'data': None}]]

    agent = json.loads(message)

    if controller.check_population():
        agent_encoded = jwt.encode(agent, 'secret', algorithm='HS256').decode('utf-8')
        controller.agents[len(controller.agents)+1] = agent_encoded
        response[1][0]['can_connect'] = True
        response[1][1]['data'] = controller.agents[len(controller.agents)]

    on_response(response[0], json.dumps(response[1]))


@socketio.on('connect_agent')
def respond_to_request(message=''):
    response = ['connection_result', {'agent_connected': False}]

    if controller.check_agent(json.loads(message)):
        if controller.check_timer():
            response[1]['agent_connected'] = True

    on_response(response[0], json.dumps(response[1]))


@socketio.on('receive_jobs')
def handle_connection(message):
    response = ['received_jobs_result', {'job_delivered': False}]

    message = json.loads(message)
    agent_method = (message['token'], (message['method'], message['parameters'][0], message['parameters'][1]))

    if controller.check_request(agent_method):
        controller.jobs[agent_method[0]] = (agent_method[1][0], agent_method[1][1], agent_method[1][2])
        response[1]['job_delivered'] = True

    on_response(response[0], json.dumps(response[1]))


@socketio.on('time_ended')
def finish_conection():
    from src.manager.simulation_instance import get_instance

    jobs = []
    for token in controller.jobs.keys():
        jobs.append((token, controller.jobs[token]))

    aux = get_instance('').do_step(jobs)

    for token, result in aux:
        on_response('job_result', json.dumps(result))
