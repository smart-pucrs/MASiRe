import sys
from subprocess import run
import os

from src.manager import simulation_instance


# Define a instancia da simulação com o arquivo inicial dela
# simulation_instance.start_manager(sys.argv[0])


# Roda o servidor flask-socketIO
project_path = os.path.dirname(os.path.realpath(__file__))
run([str(project_path) + "/venv/Scripts/python", "-m", "flask", "run"],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='0', **os.environ))

