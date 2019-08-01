import os
import re
import time
import signal
import pathlib
import requests
import subprocess
from environment_handler import Handler


def get_venv_path():
    """Get the path to the generated virtual environment.

    :return str: Path to the virtual environment system independent."""

    h = Handler()
    h.create_environment()
    return h.venv_path + 'python'


def collect_modules():
    """Get all the test modules inside the test_social_assets folder.

    Note: test modules must start with 'test_' and have the .py extension.

    :return list: List of all the test modules paths."""

    tests_dir = pathlib.Path(__file__).parent / 'test_social_assets'

    modules = []
    for (dirpath, dirnames, filenames) in os.walk(str(tests_dir.absolute())):
        for filename in filenames:
            if filename.startswith('test_') and filename.endswith('.py'):
                modules.append(str((tests_dir / filename).absolute()))

    return modules


def execute_modules():
    """Loop through all the modules executing them against the API and saving the responses.

    To execute the tests properly the simulation have to be online, any other way one is not able to pass
    through all the steps that an agent would. In order to do that, a process is popped to run the simulation itself
    and another one to run the test. When the test is completed, both the processes are killed and there is no
    remaining processes.

    :return list: All the results from the modules."""

    start_system_path = str((pathlib.Path(__file__).parents[3] / 'start_system.py').absolute())
    venv_path = get_venv_path()
    command = [venv_path, start_system_path,
               *'-conf src/tests/integration/test_social_assets/assets_test_config.json -first_t 10 -secret secret -log false'.split(' ')]

    tests_passed = []
    modules = collect_modules()
    for module in modules:
        null = open(os.devnull, 'w')
        system_proc = subprocess.Popen(command, stdout=null, stderr=subprocess.STDOUT)
        time.sleep(10)

        test_proc = subprocess.Popen([venv_path, module], stdout=subprocess.PIPE)
        out, err = test_proc.communicate()

        passed = True if re.findall('True', out.decode('utf-8')) else False
        if not passed:
            print(f'Module {module} failed')

        tests_passed.append(passed)
        test_proc.kill()

        requests.get('http://127.0.0.1:12345/terminate', json={'secret': 'secret', 'back': 0})

        requests.get('http://127.0.0.1:8910/terminate', json={'secret': 'secret', 'api': True})

        time.sleep(5)

        system_proc.kill()
        del system_proc
        time.sleep(10)

    return tests_passed


def test_system():
    """Call the function to execute all test modules and check if all the responses were True."""

    assert all(execute_modules())


if __name__ == '__main__':
    test_system()
