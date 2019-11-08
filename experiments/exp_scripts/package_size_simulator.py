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

root = str(pathlib.Path(__file__).resolve().parents[2])
temp_config = '/experiments/temp/util/temp-config.json'
default_config = '/experiments/temp/util/default-config.json'
sim_path = root + '/src/execution/simulation.py'
api_path = root + '/experiments/temp/util/fake_api.py'
reports_folder = '/experiments/temp/reports'

base_url = '192.168.1.110'
sim_port = 8910
api_port = 12345
secret = 'temp'
sim_url = f'http://{base_url}:{sim_port}'
api_url = f'http://{base_url}:{api_port}'
sim_command = ['python3', sim_path, root + temp_config, base_url, str(sim_port), str(api_port), 'true', secret]
api_command = ['python3', api_path, base_url, str(api_port), secret]

socket = socketio.Client()
sim_started = False
actions = [{'token': secret, 'action': 'pass', 'parameters': []}]
complexity_experiments = [int(n) for n in sys.argv[1:]]
results = []
default_steps = 0
exp_name = 'PACKAGE_SIZE_SIMULATOR'


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


def save_results(prob):
    path = f'{root}{reports_folder}/PACKAGE_SIZE%SIMULATOR%{str(prob)}.csv'

    with open(path, 'w+') as report:
        for e in results:
            report.write(str(e) + '\n')


@socket.on('sim_started')
def finish(msg):
    global sim_started

    sim_started = True


def set_environment_steps(prob):
    global default_steps

    log(f'{exp_name}_{prob}', 'Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['generate']['flood']['probability'] = prob
    default_steps = content['map']['steps']

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))


def start_processes(prob):
    global sim_started, results

    sim_started = False

    log(f'{exp_name}_{prob}', 'Start api process.')
    api_null = open(os.devnull, 'w')
    api_proc = subprocess.Popen(api_command, stdout=api_null, stderr=subprocess.STDOUT)

    connected = False
    while not connected:
        try:
            socket.connect(api_url)
            connected = True
        except Exception:
            time.sleep(1)

    sim_null = open(os.devnull, 'w')
    log(f'{exp_name}_{prob}', 'Start simulator process.')
    sim_proc = subprocess.Popen(sim_command, stdout=sim_null, stderr=subprocess.STDOUT)

    log(f'{exp_name}_{prob}', 'Waiting for the simulation start...')

    while not sim_started:
        time.sleep(1)

    log(f'{exp_name}_{prob}', 'Simulation started, connecting the agents...')
    requests.post(sim_url + '/register_agent', json={'token': secret, 'secret': secret})

    requests.post(sim_url + '/start', json={'secret': secret})

    log(f'{exp_name}_{prob}', 'Agents connected, processing steps...')
    for step in range(default_steps):
        response = requests.post(sim_url+'/do_actions', json={'actions': actions, 'secret': secret}).json()
        results.append(get_total_size(response))

    save_results(prob)
    results.clear()
    actions.clear()
    socket.disconnect()

    log(f'{exp_name}_{prob}', 'Simulation finished, killing all processes...')
    api_proc.kill()
    sim_proc.kill()


def log(exp, message):
    print(f'[{exp}] ## {message}')


def start_experiments():
    for prob in complexity_experiments:
        log(f'{exp_name}_{prob}', 'Start new experiment.')

        set_environment_steps(prob)
        start_processes(prob)
        time.sleep(2)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    log('FINISHED', 'Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)
