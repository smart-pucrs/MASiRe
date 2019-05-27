import requests
import socketio
import time

# Server URL           = http://127.0.0.1:12345
# Connect URL          = http://127.0.0.1:12345/connect_agent
# Validate URL         = http://127.0.0.1:12345/validate_agent
# Send job URL         = http://127.0.0.1:12345/send_job
# Receive job EVENT    = job_result_{token}
# Simulation end Event = simulation_ended

agent_data = {
    'name': 'agent1'
}

server_url = 'http://127.0.0.1:12345'
validate_url = 'http://127.0.0.1:12345/validate_agent'
send_job_url = 'http://127.0.0.1:12345/send_job'
connect_url= 'http://127.0.0.1:12345/connect_agent'

receive_job_event = 'job_result'
simulation_ended_event = 'simulation_ended'

socket_client = socketio.Client()
socket_client.connect(server_url)


response = requests.post(connect_url, json=agent_data).json()
if 'message' in response:
    exit(response['message'])

token = response['data']
namespace = response['namespace']

response = requests.post(validate_url, json=token).json()
if 'message' in response:
    exit(response['message'])

agent_info = response['info']
time.sleep(int(response['time']) + 1)


@socket_client.on(simulation_ended_event)
def simulation_ended(msg):
    socket_client.disconnect()
    print('simulation ended')
    exit()


@socket_client.on(receive_job_event, namespace=namespace)
def receive_job(msg):
    print('receive_job')


job_json = {
    'token': token,
    'action': 'pass',
    'parameters': []
}

response = requests.post(send_job_url, json=job_json).json()
if 'message' in response:
    print(response['message'])
    socket_client.disconnect()
    exit()

