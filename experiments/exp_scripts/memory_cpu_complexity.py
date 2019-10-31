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
import sys

root = str(pathlib.Path(__file__).resolve().parents[2])
temp_config = '/experiments/temp/util/temp-config.json'
default_config = '/experiments/temp/util/default-config.json'
start_system_path = root + '/start_system.py'
exp_name = 'COMPLEXITY'

base_url = '192.168.1.110'
api_port = 12345
connect_agent_url = f'http://{base_url}:{api_port}/connect_agent'
sim_command = ['python3', start_system_path,
               *(f'-conf experiments/temp/util/temp-config.json -pyv 3 -g True -url {base_url} -secret temp').split(' ')]


socket = socketio.Client()
process_finished = False
experiments = [int(n) for n in sys.argv[1:]]


@socket.on('percepts')
def finish(msg):
    global process_finished

    process_finished = True


def set_environment_steps(prob):
    log(f'{exp_name}_{prob}', 'Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['generate']['flood']['probability'] = prob

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))


def start_processes(experiment):
    global process_finished

    log(f'{exp_name}_{experiment}', 'Start report.sh process.')

    process_finished = False

    report_proc = subprocess.Popen(
        ['Desktop/DisasterSimulator/experiments/temp/util/report.sh', exp_name, str(experiment)])
    null = open(os.devnull, 'w')

    log(f'{exp_name}_{experiment}', 'Start simulator process.')

    sim_proc = subprocess.Popen(sim_command, stdout=null, stderr=subprocess.STDOUT)

    log(f'{exp_name}_{experiment}', 'Waiting for the simulation start...')

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

    log(f'{exp_name}_{experiment}', 'Simulation started, killing all processes.')

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
    for prob in experiments:
        log(f'{exp_name}_{prob}', 'Start new experiment.')

        set_environment_steps(prob)
        start_processes(prob)
        time.sleep(2)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)