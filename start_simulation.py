import sys
from subprocess import run
import os

from src.manager import SimulationInstance



#Defini a instancia da simulação com o arquivo inicial dela
SimulationInstance.start_manager(sys.argv[1])


#Roda o servidor flask-socketIO
run(["/home/mazzardo/code/ages/desastre/venv3/bin/python", "-m", "flask", "run"],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='0', **os.environ))
