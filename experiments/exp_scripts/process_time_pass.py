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
sim_path = root + '/src/execution/simulation.py'
api_path = root + '/experiments/temp/fake_api.py'
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
actions = []
complexity_experiments = [10, 100]
agents_experiments = [10,50]
results = []
default_steps = 0


def get_current_time():
    return int(round(time.time() * 1000))


def save_results(agents_amount, prob):
    file_name = f'/process_time_pass_{agents_amount}_{prob}.csv'
    path = root + reports_folder + file_name

    with open(path, 'w+') as report:
        for e in results:
            report.write(str(e) + '\n')


@socket.on('sim_started')
def finish(msg):
    global sim_started

    sim_started = True


def set_environment_steps(agents_amount, prob):
    global default_steps

    log(f'PROCESS_TIME_PASS_{agents_amount}_{prob}', 'Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['generate']['flood']['probability'] = prob
    content['agents']['drone']['amount'] = agents_amount
    default_steps = content['map']['steps']

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))


def start_processes(agents_amount, prob):
    global sim_started, results

    sim_started = False

    api_null = open(os.devnull, 'w')
    api_proc = subprocess.Popen(api_command)#, stdout=api_null, stderr=subprocess.STDOUT)

    connected = False
    while not connected:
        try:
            socket.connect(api_url)
            connected = True
        except Exception:
            time.sleep(1)

    sim_null = open(os.devnull, 'w')
    log(f'PROCESS_TIME_PASS_{agents_amount}_{prob}', 'Start simulator process.')
    sim_proc = subprocess.Popen(sim_command)#, stdout=sim_null, stderr=subprocess.STDOUT)

    log(f'PROCESS_TIME_PASS_{agents_amount}_{prob}', 'Waiting for the simulation start...')

    while not sim_started:
        time.sleep(1)

    connect_agents(agents_amount)

    requests.post(sim_url + '/start', json={'secret': secret})

    for step in range(default_steps):
        old_time = get_current_time()
        response = requests.post(sim_url+'/do_actions', json={'actions': actions, 'secret': secret}).json()
        new_time = get_current_time()
        results.append(new_time - old_time)

    save_results(agents_amount, prob)
    results.clear()
    actions.clear()
    socket.disconnect()

    current_process = psutil.Process(sim_proc.pid)
    children = current_process.children(recursive=True)
    for child in children:
        os.kill(child.pid, signal.SIGTERM)

    current_process = psutil.Process(api_proc.pid)
    children = current_process.children(recursive=True)
    for child in children:
        os.kill(child.pid, signal.SIGTERM)

    api_proc.kill()
    sim_proc.kill()


def log(exp, message):
    print(f'[{exp}] ## {message}')


def connect_agents(agents_amount):
    for agent in range(agents_amount):
        token = f'temp{agent}'
        requests.post(sim_url+'/register_agent', json={'token': token, 'secret': secret})
        actions.append({'token': token, 'action': 'pass', 'parameters': []})


def start_experiments():
    for agents_amount in agents_experiments:
        for prob in complexity_experiments:
            log(f'PROCESS_TIME_PASS_{agents_amount}_{prob}', 'Start new experiment.')

            set_environment_steps(agents_amount, prob)
            start_processes(agents_amount, prob)
            time.sleep(2)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)
