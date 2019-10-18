import sys
import os
import signal
import shutil
import time
import json
import subprocess
import pathlib

def set_steps(steps):
    with open(ROOT + TEMP_FILE_PATH, 'r') as config:
        content = json.loads(config.read())

    content['map']['steps'] = steps

    with open(ROOT + TEMP_FILE_PATH, 'w') as config:
        config.write(json.dumps(content, sort_keys=False, indent=4))

ROOT = str(pathlib.Path(__file__).parents[2])
TEMP_FILE_PATH = '/experiments/temp-config.json'
DEFAULT_CONFIG_PATH = ROOT + '/experiments/default-config.json'
STEPS_BY_ITERATIONS = [50,150,300,450,600,750,900]

start_system_path = ROOT + '/start_system.py'
#venv_path = get_venv_path()
command = ['python3', start_system_path,
               *'-conf experiments/temp-config.json'.split(' ')]

# Create temp config file to run this script
shutil.copy2(DEFAULT_CONFIG_PATH, ROOT + TEMP_FILE_PATH)

set_steps(10)
process = subprocess.run(command)
print(process)


