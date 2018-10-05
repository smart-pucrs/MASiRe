import sys
from subprocess import run
import os

# Defini a instancia da simulação com o arquivo inicial dela
from src.manager import SimulationInstance

# Roda o servidor flask-socketIO
run(["/home/mazzardo/code/ages/desastre/venv3/bin/python", "-m", "flask", "run"],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='1', **os.environ))
