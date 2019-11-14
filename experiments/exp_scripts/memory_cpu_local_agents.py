import socketio
import requests
import signal
import time
import sys
import os

url = sys.argv[1]
server_url = f'http://{url}:12345'
register_event = 'register_agent'
connect_agent_url = f'{server_url}/connect_agent'
finished_process = False
agents_amounts = [int(n) for n in sys.argv[2:]]
agent_name = 'fake_agent'
agents = {}

socket = socketio.Client()

@socket.on('percepts')
def finish_experiment(msg):
    global finished_process

    finished_process = True


def init_agents_connections():
    global finished_process

    for agents_amount in agents_amounts:
        for agent in range(agents_amount - 2):
            agents[agent_name + str(agent)] = socketio.Client()

        response = dict(result=False)
        while not response['result']:
            try:
                response = requests.post(connect_agent_url, json={'name': 'last'}).json()
            except Exception:
                pass

        socket.connect(server_url)
        socket.emit(register_event, data=dict(token=response['message']))

        for agent in agents:
            response = dict(result=False)

            while not response['result']:
                try:
                    response = requests.post(connect_agent_url, json={'name': agent}).json()
                except Exception:
                    pass

            agents[agent].connect(server_url)
            agents[agent].emit(register_event, data=dict(token=response['message']))

        while not finished_process:
            time.sleep(1)

        socket.disconnect()
        agents.clear()
        finished_process = False

    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    init_agents_connections()
