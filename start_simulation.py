import os
import pathlib
from subprocess import run
from src.manager.simulation_instance import SimulationSingleton


# Define the instance of the simulation with its startup file
def start_instance():
    SimulationSingleton('files/config.json').simulation_manager


# Here are setted the directory at venv where the python executable are
def start_simulation():
    interpreter_path = str(pathlib.Path(__file__).parent.absolute())

    # Windows based OS
    if os.name == 'nt':
        interpreter_path += '\\venv\\Scripts\\python.exe'

    # Linux based OS
    else:
        interpreter_path += "/venv/bin/python"

    run([str(interpreter_path), "-m", "flask", "run", "--host=0.0.0.0"],
        env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='1', **os.environ))


if __name__ == '__main__':
    start_instance()
    start_simulation()
