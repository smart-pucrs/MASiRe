import json
import os
import pathlib
import subprocess
from multiprocessing import Process
from src.startup.environment_handler import Handler
from src.startup.watch_arguments_parser import Parser
from src.startup.configuration_checker import Checker


def start_monitor(module_path, monitor_args, venv_path, py_version):
    """Start the MONITOR by command line."""

    subprocess.call([f"{str(venv_path)}python{py_version}", module_path, *map(str, monitor_args)])


if __name__ == '__main__':
    parser = Parser()
    env_handler = Handler()

    monitor_arguments, python_version = parser.get_arguments()
    env_handler.create_environment('', python_version)

    monitor_path = os.getcwd() + '/src/execution/monitor.py'
    monitor_process_arguments = (monitor_path, monitor_arguments, env_handler.venv_path, python_version)
    monitor_process = Process(target=start_monitor, args=monitor_process_arguments, daemon=True)

    subprocess.call([f"{str(env_handler.venv_path)}python{python_version}", monitor_path, *map(str, monitor_arguments)])

    monitor_process.start()
    monitor_process.join()
