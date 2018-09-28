from socketIO_client import SocketIO, LoggingNamespace
import json

agent_denied = {
    "Name": "Toyota",
    "Version": "1.3",
    "Type": "Car",
    "Owner": "87462"
}

agent_accepted = {
    "Name": "Toyot",
    "Version": "1.3",
    "Type": "Car",
    "Owner": "87462"
}

step_config_agent = {
    'id': 'Ubuntu',
    'method': 'move',
    'parameters': ['24', '32']
}


def on_response(args):
    print('Response: ', args)


def on_response_jobs(args):
    print('Response: ', args)


socketIO = SocketIO('localhost', 5000, LoggingNamespace)
socketIO.on('connection_result', on_response)
socketIO.emit('connect', json.dumps(agent_accepted))

socketIO.on('received_jobs_result', on_response_jobs)
socketIO.emit('receive_jobs', json.dumps(step_config_agent))
socketIO.wait(seconds=1)
