import sys
from subprocess import run
import os

from src.manager import simulation_instance


# Define a instancia da simulação com o arquivo inicial dela
simulation_instance.get_instance('config.json')


'''
    O complemento APOS o USERPROFILE eh o caminho para o virtualenv da maquina que o criou, caso haja problemas
    O caminho até o .virtualenvs eh padrao para todas as maquinas, verificar o nome da pasta contendo 'desastres'
    no nome e substituir o nome visto pelo nome 'desastres-8vkced-v'
'''

# Roda o servidor flask-socketIO
project_path = os.environ['USERPROFILE'] + "/.virtualenvs/desastres-8vkced-v/scripts/python"
run([str(project_path), "-m", "flask", "run", "--host=0.0.0.0"],
    env=dict(FLASK_APP='src/app.py', FLASK_ENV='development', FLASK_DEBUG='1', **os.environ))
