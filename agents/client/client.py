from socketIO_client import SocketIO, LoggingNamespace
import json


# ==================== ATENTION, ALL THE LISTEN EVENTS WERE CHANGED ===========================


agent = {
    "name": "Toyota",
    "version": "1.3",
    "type": "Car",
    "owner": "87462"
}

token = None
response_ready = False
response_connect = False
response_job = False


def on_response_job_result(args):
    print("to be or not to be")
    print(args)


def on_response_jobs(args):
    print('Response: ', json.loads(args))


def on_response_connection(args):
    global response_connect

    if 'token' in args:
        socketIO.emit('receive_jobs', json.dumps(step_config_agent))

    response_connect = True
    print('Response: ', json.loads(args))


def on_response_ready(args):
    global token, response_ready

    response_ready = True
    args = json.loads(args)

    token = args[1]['data']
    print('Response: ', args[0])


socketIO = SocketIO('localhost', 5000, LoggingNamespace)
socketIO.on('ready', on_response_ready)
socketIO.emit('first_message', json.dumps(agent))

socketIO.wait(2)

agent_token = {
    "token": token,
    "version": "1.3",
    "type": "Car",
    "owner": "87462"
}

socketIO.on('connection_result', on_response_connection)
socketIO.emit('connect_agent', json.dumps(agent_token))

socketIO.wait(2)

step_config_agent = {
    'token': token,
    'action': 'move',
    'parameters': ['24', '32']
}

event = 'job_result'

socketIO.on('received_jobs_result', on_response_jobs)
socketIO.on('jobs_result', on_response_job_result)
socketIO.emit('receive_jobs', json.dumps(step_config_agent))

socketIO.wait(60)

print(token)
