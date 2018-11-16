import sys
from subprocess import run
import os

from src.manager import simulation_instance


# Define the instance of the simulation with its startup file
simulation_instance.get_instance('config.json')


'''
    The path after USERPROFILE depends on each computer
    To properly use the simulation configure the path to the correct for your computer 
'''

# Run the flask socketIO server

project_path = os.getcwd()\

if os.name == 'nt':
    project_path += '\\venv\\Scripts\\python.exe'
else:
    project_path += "/venv/bin/python"

run([str(project_path), "-m", "flask", "run", "--host=0.0.0.0"],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='1', **os.environ))
