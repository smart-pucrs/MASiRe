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

agent_data2 = {
    'name': 'agent2'
}

server_url = 'http://127.0.0.1:12345'
validate_url = 'http://127.0.0.1:12345/validate_agent'
send_job_url = 'http://127.0.0.1:12345/send_action'
connect_url = 'http://127.0.0.1:12345/connect_agent'
initial_percepts_event = 'initial_percepts'
receive_job_event = 'action_result'
send_job_event = 'send_action'
match_ended_event = 'match_ended'
simulation_result_event = 'simulation_result'
send_job_result_event = 'send_action_result'


socket_client = socketio.Client()
socket_client.connect(server_url, agent_data)
socket_client2 = socketio.Client()
socket_client2.connect(server_url, agent_data2)

# Connect the agent in the server
response = requests.post(connect_url, json=agent_data).json()
response2 = requests.post(connect_url, json=agent_data2).json()
print(response)
print(response2)

token = response['data']
token2 = response2['data']

# Validate the agent in the server
response = requests.post(validate_url, json=token).json()
response2 = requests.post(validate_url, json=token2).json()
print(response)
print(response2)

# Register the agent in the server
socket_client.emit('register', json.dumps(agent_data))
socket_client2.emit('register', json.dumps(agent_data2))


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

    msg = json.loads(msg)

    if msg['environment']['step'] == 0:
        socket_client.emit('send_action', json.dumps({'token': token, 'action': 'carry_agent', 'parameters': [token2]}))


@socket_client2.on(initial_percepts_event)
def initial_percepts(msg):
    print("map_percepts -> ", msg)


@socket_client2.on(match_ended_event)
def match_ended(msg):
    print(f'\n{msg}\n')


@socket_client2.on(simulation_result_event)
def simulation_result(msg):
    print('\n' + msg + '\n')


@socket_client2.on(send_job_result_event)
def send_job_result(message):
    print('\n' + json.dumps(message) + '\n')


@socket_client2.on(receive_job_event)
def receive_job(msg):
    print('\n'+msg+'\n')

    msg = json.loads(msg)

    if msg['environment']['step'] == 0:
        socket_client2.emit('send_action', json.dumps({'token': token2, 'action': 'carry_request', 'parameters': [token]}))

