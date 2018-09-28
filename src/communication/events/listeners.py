import _thread
import time

import jwt
from flask import jsonify, json
from flask_socketio import emit

from src.communication.ActionResult import ActionResult
from src.__init__ import socketio
from src.communication.events.emiters import response_to_action
from src.communication.events.prepare_action import verify_method
from src.communication.AgentManager import AgentManager

agent_manager = AgentManager()


@socketio.on('receive_jobs')
def handle_connection(message):
    agent = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    method = agent['method']
    emit('received_jobs_result', verify_method(method, agent))


@socketio.on('connect')
def respond_to_request(message=None):
    global init
    init = time.time()
    _thread.start_new_thread(start_timer, (None,))
    time.sleep(5)
    emit('connection_result', {'success': True})
    if not retorno:
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
    global retorno
    while 1:
        if time.time() - init > 3:
            retorno = False
            break
