import os
import signal
import shutil
import time
import subprocess
import pathlib
import socketio
import requests
import json
import psutil

root = str(pathlib.Path(__file__).resolve().parents[2])
temp_config = '/experiments/temp/temp-config.json'
default_config = '/experiments/temp/default-config.json'
start_system_path = root + '/start_system.py'

base_url = '192.168.1.110'
api_port = 12345
connect_agent_url = f'http://{base_url}:{api_port}/connect_agent'
sim_command = ['python3', start_system_path,
               *(f'-conf experiments/temp/temp-config.json -pyv 3 -g True -url {base_url} -secret temp -first_t 50').split(' ')]

socket = socketio.Client()
process_finished = False
experiments = [10, 20]


@socket.on('percepts')
def finish(msg):
    global process_finished

    process_finished = True


def set_environment_agents(agents):
    log(f'AGENTS_{agents}', 'Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['agents']['drone']['amount'] = agents + 1
    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))


def start_processes(experiment):
    global process_finished

    log(f'AGENTS_{experiment}', 'Start script-report.sh process.')

    process_finished = False

    report_proc = subprocess.Popen(
        ['Desktop/DisasterSimulator/experiments/temp/script-report.sh', 'AGENTS', str(experiment)])

    log(f'AGENTS_{experiment}', 'Start simulator process.')

    null = open(os.devnull, 'w')
    sim_proc = subprocess.Popen(sim_command, stdout=null, stderr=subprocess.STDOUT)

    log(f'AGENTS_{experiment}', 'Waiting for the simulation start...')

    response = dict(result=False)
    while not response['result']:
        time.sleep(1)
        try:
            response = requests.post(connect_agent_url, json={'name': 'temp'}).json()
        except Exception:
            pass

    socket.connect(f'http://{base_url}:{api_port}')
    socket.emit('register_agent', data=dict(token=response['message']))

    while not process_finished:
        time.sleep(1)
    time.sleep(5)

    log(f'AGENTS_{experiment}', 'Simulation started, killing all processes.')

    current_process = psutil.Process(sim_proc.pid)
    children = current_process.children(recursive=True)
    for child in children:
        os.kill(child.pid, signal.SIGTERM)

    socket.disconnect()
    report_proc.kill()
    sim_proc.kill()

    del report_proc
    del sim_proc


def log(exp, message):
    print(f'[{exp}] ## {message}')


def start_experiments():
    for agents in experiments:
        log(f'AGENTS_{agents}', 'Start new experiment.')

        set_environment_agents(agents)
        start_processes(agents)
        time.sleep(2)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)