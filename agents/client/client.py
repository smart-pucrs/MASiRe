from socketIO_client import SocketIO, LoggingNamespace
import json


agent = {
    "Name": "Toyota",
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


socketIO = SocketIO('localhost', 5000, LoggingNamespace)
socketIO.on('connection_result', on_response)
socketIO.emit('connect', json.dumps(agent))

socketIO.on('received_jobs_result', on_response)
socketIO.on('jobs_result', on_response)
socketIO.emit('receive_jobs', json.dumps(step_config_agent))

socketIO.wait(seconds=3)
