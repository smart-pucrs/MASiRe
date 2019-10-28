import sys
import os
import signal
import shutil
import time
import json
import subprocess
import pathlib
import socketio
import requests
import json
import psutil
from multiprocessing import Process


root = str(pathlib.Path(__file__).resolve().parents[2])
temp_config = '/experiments/temp/temp-config.json'
default_config = '/experiments/temp/default-config.json'
start_system_path = root + '/start_system.py'

base_url = '192.168.1.110'
api_port = 12345
connect_agent_url = f'http://{base_url}:{api_port}/connect_agent'
sim_command = ['python3', start_system_path, *(f'-conf experiments/temp/temp-config.json -pyv 3 -g True -url {base_url} -secret temp').split(' ')]

experiments = {
    'STEPS':{
        'config_command': 'set_environment_steps(args, idx)',
        'args': [10],
    },
    'MAPS':{
        'config_command': 'set_environment_maps(args, idx)',
        'args': [{
            'name': 'map1',
            'osm': 'experiments/temp/maps/brumadinho.osm',
            'minLat': -20.1726,
            'minLon': -44.2104,
            'maxLat': -20.1136,
            'maxLon': -44.1102,
            'centerLon': -44.1603,
            'centerLat': -20.1431
            }]
    },
    'COMPLEXITY': {
        'config_command': 'set_environment_complexity(args, idx)',
        'args': [1]
    },
    'AGENTS':{
        'config_command': 'set_environment_agents(args, idx)',
        'args': [10,50,100]
    }
}

socket = socketio.Client()
process_finished = False

@socket.on('percepts')
def finish(msg):
    global process_finished

    process_finished = True

def set_environment_steps(steps, idx):
    log(f'STEPS_{idx}','Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['map']['steps'] = steps

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

def set_environment_complexity(prob, idx):
    log(f'COMPLEXITY_{idx}','Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['generate']['flood']['probability'] = prob
    
    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

def set_environment_maps(map_config, idx):
    log(f'MAPS_{idx}','Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['map']['maps'] = [map_config]

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

def set_environment_agents(agents_amount, idx):
    log(f'AGENTS_{idx}','Setting the environment.')
    with open(root + default_config, 'r') as config:
        content = json.loads(config.read())

    content['agents']['drone'] = agents_amount+1

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

def start_processes(experiment, idx):
    global process_finished

    log(f'{experiment}_{idx}', 'Start script-report.sh process.')
    
    process_finished = False

    report_proc = subprocess.Popen(['Desktop/DisasterSimulator/experiments/temp/script-report.sh',experiment,str(idx)])
    null = open(os.devnull, 'w')

    log(f'{experiment}_{idx}', 'Start simulator process.')
    
    sim_proc = subprocess.Popen(sim_command, stdout=null, stderr=subprocess.STDOUT)
    
    log(f'{experiment}_{idx}','Waiting for the simulation start...')

    response = dict(result=False)
    while(not response['result']):
        time.sleep(1)
        try:
            response = requests.post(connect_agent_url, json={'name': 'temp'}).json()
        except Exception:
            pass
    
    socket.connect(f'http://{base_url}:{api_port}')
    socket.emit('register_agent', data=dict(token=response['message']))

    while(not process_finished):
        time.sleep(1)
    time.sleep(5)

    log(f'{experiment}_{idx}','Simulation started, killing all processes.')

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
    for experiment in experiments:
        log(experiment,'Start new experiment.')
        
        for idx, args in enumerate(experiments[experiment]['args']):
            exec(experiments[experiment]['config_command'])
            start_processes(experiment, idx)
            time.sleep(2)


if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)