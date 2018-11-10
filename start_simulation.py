import sys
from subprocess import run
import os

from src.manager import simulation_instance


# Define a instancia da simulação com o arquivo inicial dela
# simulation_instance.start_manager(sys.argv[0])


# Roda o servidor flask-socketIO
project_path = '/home/15280414/.local/share/virtualenvs/Desastres-ROaEGa36/bin/python3.6'
run([str(project_path), "-m", "flask", "run", '--host=0.0.0.0'],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='1', **os.environ))

