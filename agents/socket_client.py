import requests
import json
import socketio
import time

# Server URL           = http://127.0.0.1:12345
# Connect URL          = http://127.0.0.1:12345/connect_agent
# Validate URL         = http://127.0.0.1:12345/validate_agent
# Send job URL         = http://127.0.0.1:12345/send_job
# Receive job EVENT    = job_result
# Simulation end Event = simulation_ended

agent_data = {
    'name': 'agent1'
}

server_url = 'http://127.0.0.1:12345'
validate_url = 'http://127.0.0.1:12345/validate_agent'
send_job_url = 'http://127.0.0.1:12345/send_job'
connect_url = 'http://127.0.0.1:12345/connect_agent'
initial_percepts_event = 'initial_percepts'
receive_job_event = 'job_result'
send_job_event = 'send_job'
match_ended_event = 'match_ended'
simulation_result_event = 'simulation_result'
send_job_result_event = 'send_job_result'

socket_client = socketio.Client()
socket_client.connect(server_url, agent_data)

# Connect the agent in the server
response = requests.post(connect_url, json=agent_data).json()
print(response)
if 'message' in response:
    exit(response['message'])

token = response['data']

# Validate the agent in the server
response = requests.post(validate_url, json=token).json()
print(response)
if 'message' in response:
    exit(response['message'])

# Register the agent in the server
socket_client.emit('register', json.dumps({'name': 'agent1'}))


@socket_client.on(initial_percepts_event)
def initial_percepts(msg):
    print("map_percepts -> ", msg)


@socket_client.on(match_ended_event)
def match_ended(msg):
    print(f'\n{msg}\n')


@socket_client.on(simulation_result_event)
def simulation_result(msg):
    print('\n' + msg + '\n')


@socket_client.on(send_job_result_event)
def send_job_result(message):
    print('\n' + json.dumps(message) + '\n')


@socket_client.on(receive_job_event)
def receive_job(msg):
    print('\n'+msg+'\n')


job_json = {
    'token': token,
    'action': 'rescue_victim',
    'parameters': []
}

time.sleep(4)
socket_client.emit(send_job_event, job_json)

job_json['action'] = 'deliver_physical'
job_json['parameters'] = ['victim', 1]

time.sleep(1)
socket_client.emit(send_job_event, job_json)

# Send one job to the server
# response = requests.post(send_job_url, json=job_json).json()
# print(response)
# if 'message' in response:
#     print(response['message'])
#     socket_client.disconnect()
#     print('FIM!!')
#     exit()