import os
import re
import time
import pathlib
import requests
import subprocess
import socketio
from environment_handler import Handler

socket = socketio.Client()


def get_venv_path():
    h = Handler()
    h.create_environment()
    return h.venv_path + 'python'


def collect_scripts():
    scripts_dir = pathlib.Path(__file__).resolve().parent / 'scripts'
    scripts = []

    for (dirpath, dirnames, filenames) in os.walk(str(scripts_dir.absolute())):
        for filename in filenames:
            if filename.startswith('script_') and filename.endswith('.py'):
                scripts.append((str((scripts_dir / filename).absolute()), filename))
    return scripts


def init_experiments():
    venv_path = get_venv_path()
    scripts = collect_scripts()

    for script, script_name in scripts:
        script_proc = subprocess.Popen([venv_path, script], stdout=subprocess.PIPE)
        out, err = script_proc.communicate()

        passed = True if re.findall('True', out.decode('utf-8')) else False
        if not passed:
            print(f'{script_name} ... failed')
        else:
            print(f'{script_name} ... finished')

        script_proc.kill()
        time.sleep(1)

    print('All scripts processed!!!')


if __name__ == '__main__':
    init_experiments()
