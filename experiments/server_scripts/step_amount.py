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
temp_config = '/experiments/temp-config.json'
default_config = '/experiments/default-config.json'
start_system_path = root + '/start_system.py'
command = ['python3', start_system_path, *'-conf experiments/temp-config.json -pyv 3 -g True -url 192.168.1.110 -secret temp'.split(' ')]

steps = [50, 150]
socket = socketio.Client()
process_finished = False

@socket.on('percepts')
def finish(msg):
    global process_finished

    process_finished = True

def set_environment(steps):
    log(steps,'Setting the environment.')
    with open(root + temp_config, 'r') as config:
        content = json.loads(config.read())

    content['map']['steps'] = steps
    content['agents']['drone']['amount'] = 1

    with open(root + temp_config, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

def start_processes(number_steps):
    global process_finished

    log(number_steps, 'Start script-report.sh process.')
    
    process_finished = False

    report_proc = subprocess.Popen(['Desktop/DisasterSimulator/experiments/server_scripts/script-report.sh','steps',str(number_steps)])
    null = open(os.devnull, 'w')

    log(number_steps, 'Start simulator process.')
    
    sim_proc = subprocess.Popen(command, stdout=null, stderr=subprocess.STDOUT)
    

    log(number_steps,'Waiting for the simulation start...')

    response = dict(result=False)
    while(not response['result']):
        time.sleep(1)
        try:
            response = requests.post('http://192.168.1.110:12345/connect_agent', json={'name': 'temp'}).json()
        except Exception:
            pass
    
    socket.connect('http://192.168.1.110:12345')
    socket.emit('register_agent', data=dict(token=response['message']))

    while(not process_finished):
        time.sleep(1)
    time.sleep(5)

    log(number_steps,'Simulation started, killing all processes.')

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
    print(f'[STEPS_{exp}] ## {message}')

def start_experiments():
    for it in steps:
        log(it,'Start new experiment.')
        
        set_environment(it)
        start_processes(it)
        time.sleep(2)

if __name__ == '__main__':
    # Create temp file to run the experiments
    shutil.copy2(root + default_config, root + temp_config)
    # Start the first experiment
    start_experiments()

    print('[FINISHED] ## Finished all experiments')
    os.kill(os.getpid(), signal.SIGTERM)