
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from agents.src.simulation import Simulation
from agents.src.ActionResult import ActionResult
from agents.src.AgentManager import AgentManager

import _thread
import json
import jwt
import logging
import time

retorno = True
simulation = Simulation('')
agent_manager = AgentManager()

app = Flask(__name__)
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CORS(app)

agents = [{}]

init = 0


@socketio.on('receive_jobs')
def handle_connection(message):
    agent = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    method = agent['method']
    emit('received_jobs_result', verify_method(method, agent))


def verify_method(method, agent):
    if method == 'deliver_virtual':
        return deliver_physical_load(agent)

    elif method == 'deliver_physical':
        return deliver_physical_load(agent)

    elif method == 'photograph':
        return post_photograph(agent)

    elif method == 'analyze_photo':
        return analyze_photo(agent)

    elif method == 'rescue victim':
        return rescue_victim(agent)

    elif method == 'collect water':
        return collect_water_sample(agent)

    elif method == 'move':
        return move(agent)


def handle_request(agent):
    if verify_json(agent):
        agents.append(agent)
        return 'agent added to done jobs list'


def verify_json(agent):
    f = open('agents.json', 'r').read()
    json_string = f.rstrip()
    available_agents = json.loads(json_string)

    if agent['parameters'] == '' or agent['parameters'] is None:
        return False

    if not agentispresent(agent, available_agents['agents']):
        return False

    return True


def agentispresent(agent, agents_list):
    for ag in agents_list:
        if ag['Name'] == agent['id']:
            return True

    return False


# =========================== Rotas =========================== #


# ================= Virtual load function ============= #
def deliver_virtual_load(agent):
    return handle_request(agent)


# ================ Physical load function ============== #
def deliver_physical_load(agent):
    return handle_request(agent)


# ================== Photograph functions =============== #
def post_photograph(agent):
    return handle_request(agent)


def analyze_photo(agent):
    return handle_request(agent)


# ===================== Victim function ================= #
def rescue_victim(agent):
    return handle_request(agent)


# =================== Water function ================= #
def collect_water_sample(agent):
    return handle_request(agent)


# ============== Move function ============= #
def move(agent):
    return handle_request(agent)


# ============== Send jobs ================= #
def send_jobs():
    return jsonify(simulation.get_jobs())


# =================MAIN=============== #


@app.route('/list')
def list_agents():
    data = request.get_data()
    f = open('agents.json', 'r').read()
    json_string = f.rstrip()
    available_agents = json.loads(json_string)

    return jsonify(available_agents)


@app.route('/requestConnection', methods=['POST'])
def connect():
    agent = request.get_json()
    print(agent)
    encoded = jwt.encode(agent, 'secret', algorithm='HS256')
    response = {
        "encoded": encoded.decode('utf-8'),
        "ip": '127.0.0.1',
        "port": 5000
    }
    return jsonify(response)


@socketio.on('connect')
def respond_to_request(message=None):
    global init
    init = time.time()
    _thread.start_new_thread(start_timer, (None,))
    time.sleep(5)
    emit('connection_result', {'success': retorno})
    if not retorno:
        # socketio.
        pass


def start_timer(input = None):
    global retorno
    while 1:
        if time.time() - init > 3:
            retorno = False
            break


@socketio.on('ready')
def respond_to_request2(message):
    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)
    agent_manager.manage_agents(decoded)
    action_result = [ActionResult(message['data'], 'Let it be'), ActionResult(message['data'], 'Let it be2'), ActionResult(message['data'], 'Let it be3')]
    call_responses(action_result)


def ack():
    print('message was received!')


def response_to_action(response, token):
    emit(token, response, callback=ack)


def call_responses(results):
    for result in results:
        response_to_action(result.response, result.token)


if __name__ == '__main__':
    logger.info('Running socket IO')
    socketio.run(app)
