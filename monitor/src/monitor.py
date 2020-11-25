import sys
import time
import requests
import logging
import toml
from werkzeug.serving import run_simple
from flask import Flask, render_template
from addict import Dict
from helpers.logger import Logger
from flask_restful import Api
from resources.manager import SimulationManager, MatchInfoManager, MatchStepManager

PATH_TEMPLATES = 'graphic_interface/templates'
PATH_STATIC = 'graphic_interface/static'
PATH_CONFIG = 'monitor/config.toml'

logging.basicConfig(format="[MONITOR] [%(levelname)s] %(message)s",level=logging.DEBUG)
logging.getLogger(__name__)

app = Flask(__name__, template_folder=PATH_TEMPLATES, static_folder=PATH_STATIC)
api = Api(app)

config = Dict(toml.load(PATH_CONFIG))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    stacktrace = logging.getLogger('werkzeug')
    stacktrace.disabled = True

    arguments = sys.argv[1:]
    if len(arguments) == 1:
         sim_args = {'simulation_config': None, 'to_record': config.record, 'replay_file_name': arguments[0]}
    else:
        while True:
            try:
                response = requests.get(f'http://{config.api.url}:{config.api.port}/sim_config').json()
                sim_args = {'simulation_config': response, 'to_record': config.record}
                break
            except requests.exceptions.ConnectionError:
                Logger.error('Error to connect the monitor socket to API.')
                Logger.error('Try to connect again...')

                time.sleep(1)
            except Exception as e:
                Logger.critical(f'Unknown error: {str(e)}')
                Logger.error('Try to connect again...')

                time.sleep(1)

    api.add_resource(SimulationManager, '/simulator/info/<string:id_attribute>',
                     endpoint='sim_info',
                     resource_class_kwargs=sim_args)
    api.add_resource(MatchStepManager,
                     '/simulator/match/<int:match>/step',
                     '/simulator/match/<int:match>/step/<int:step>',
                     endpoint='step')
    api.add_resource(MatchInfoManager, '/simulator/match/<int:match>/info/<string:id_attribute>',
                     endpoint='match')

    Logger.normal(f'Graphic Interface: Serving on http://{config.monitor.url}:{config.monitor.port}')
    run_simple(application=app, hostname=config.monitor.url, port=int(config.monitor.port), use_debugger=False)
