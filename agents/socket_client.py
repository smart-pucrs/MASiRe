import requests
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

server_url = 'http://127.0.0.1:12346'
validate_url = 'http://127.0.0.1:12346/validate_agent'
send_job_url = 'http://127.0.0.1:12346/send_job'
connect_url = 'http://127.0.0.1:12346/connect_agent'
receive_job_event = 'job_result'
simulation_ended_event = 'simulation_ended'


socket_client = socketio.Client()
socket_client.connect(server_url, agent_data)

# Connect the agent in the server
response = requests.post(connect_url, json=agent_data).json()
if 'message' in response:
    exit(response['message'])

token = response['data']

# Validate the agent in the server
response = requests.post(validate_url, json=token).json()
if 'message' in response:
    exit(response['message'])

time.sleep(response['time'] + 1)
agent_info = response['info']


@socket_client.on(simulation_ended_event)
def simulation_ended(msg):
    socket_client.disconnect()
    print('simulation ended')
    exit()


@socket_client.on(receive_job_event)
def receive_job(msg):
    print('receive_job')
    print(msg)


job_json = {
    'token': token,
    'action': 'pass',
    'parameters': []
}

# Send one job to the server
response = requests.post(send_job_url, json=job_json).json()
if 'message' in response:
    print(response['message'])
    socket_client.disconnect()
    print('FIM!!')
    exit()

