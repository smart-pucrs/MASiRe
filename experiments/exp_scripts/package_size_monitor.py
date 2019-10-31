import os
import signal
import shutil
import time
import subprocess
import pathlib
import socketio
import requests
import json
import sys
import psutil

root = str(pathlib.Path(__file__).resolve().parents[2])
temp_config = '/experiments/temp/util/temp-config.json'
default_config = '/experiments/temp/util/default-config.json'
reports_folder = '/experiments/temp/reports'
start_system_path = root + '/start_system.py'

base_url = '192.168.1.110'
api_port = 12345
sim_port = 8910
secret = 'temp'
connect_agent_url = f'http://{base_url}:{api_port}/connect_agent'
connect_monitor_url = f'http://{base_url}:{api_port}/connect_monitor'
sim_command = ['python3', start_system_path,
               *f'-conf {root+temp_config} -pyv 3 -g True -url {base_url} -secret {secret} -first_t 20'.split(' ')]
exp_name = 'PACKAGE_SIZE_API'

agent_socket = socketio.Client()
monitor_socket = socketio.Client()
agent_token = None
monitor_token = None
agent_package_sizes = []
monitor_package_sizes = []

process_finished = False
experiments = [100, 100]
current_prob = None


@monitor_socket.on('percepts')
def percepts(msg):
    global monitor_package_sizes
    #
    # msg_size = get_total_size(msg)
    # monitor_package_sizes.append(msg_size)
    agent_socket.emit('send_action', json.dumps({'token': agent_token, 'action': 'pass', 'parameters': []}))


@monitor_socket.on('bye')
def finish(msg):
    global process_finished
    # global monitor_package_sizes
    #
    # path = root + reports_folder + '/package_size_api_monitor_' + str(current_prob) + '.csv'
    #
    # with open(path, 'w+') as report:
    #     for e in monitor_package_sizes:
    #         report.write(str(e)+'\n')
    #
    process_finished = True


def get_total_size(data):
    total = 0
    if isinstance(data, list):
        for each in data:
            if isinstance(each, dict) or isinstance(each, list):
                total += get_total_size(each)
            else:
                total += sys.getsizeof(each)
    elif isinstance(data, dict):
        for each in data.values():
            if isinstance(each, dict) or isinstance(each, list):
                total += get_total_size(each)
            else:
                total += sys.getsizeof(each)
    else:
        total += sys.getsizeof(data)

    return total


def set_environment_steps(prob):
    global current_prob
    current_prob = prob

    log(f'{exp_name}_{prob}', 'Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['generate']['flood']['probability'] = prob

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))


def start_processes(experiment):
    global process_finished

    process_finished = False

    null = open(os.devnull, 'w')
    log(f'{exp_name}_{experiment}', 'Start simulator process.')

    sim_proc = subprocess.Popen(sim_command)#, stdout=null, stderr=subprocess.STDOUT)

    log(f'{exp_name}_{experiment}', 'Waiting for the simulation start...')

    connect_monitor()
    connect_agent()

    while not process_finished:
        time.sleep(1)

    monitor_socket.disconnect()
    monitor_package_sizes.clear()

    log(f'{exp_name}_{experiment}', 'Simulation finished, killing all processes.')

    time.sleep(5)

    # current_process = psutil.Process(sim_proc.pid)
    # children = current_process.children(recursive=True)
    # for child in children:
    #     os.kill(child.pid, signal.SIGTERM)
    #
    # sim_proc.kill()

    sim_proc.kill()
    del sim_proc
    time.sleep(10)


def connect_agent():
    global agent_socket
    global agent_token

    response = dict(result=False)
    while not response['result']:
        time.sleep(1)
        try:
            response = requests.post(connect_agent_url, json={'name': 'temp'}).json()
            agent_token = response['message']
        except Exception:
            continue

    agent_socket.connect(f'http://{base_url}:{api_port}')
    agent_socket.emit('register_agent', data=dict(token=agent_token))


def connect_monitor():
    connected = False

    while not connected:
        time.sleep(1)
        try:
            monitor_socket.connect(f'http://{base_url}:{api_port}')
            connected = True
        except Exception:
            continue

    monitor_socket.emit('connect_monitor', data=dict())


def log(exp, message):
    print(f'[{exp}] ## {message}')


def start_experiments():
    for prob in experiments:
        log(f'{exp_name}_{prob}', 'Start new experiment.')

        set_environment_steps(prob)
        start_processes(prob)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)