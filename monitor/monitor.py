import sys
import time
import requests
import logging
from werkzeug.serving import run_simple
from flask import Flask, render_template
from monitor_engine.helpers.logger import Logger
from flask_restful import Api
from monitor_engine.resources.manager import SimulationManager, MatchInfoManager, MatchStepManager

logging.basicConfig(format="[MONITOR] [%(levelname)s] %(message)s",level=logging.DEBUG)
logging.getLogger(__name__)

arguments = sys.argv[1:]
print("All: ",arguments)
if len(arguments) == 3:
    replay, base_url, monitor_port = arguments
    replay_mode = True
else:
    base_url, monitor_port, api_port, record, config, secret = sys.argv[1:]
    replay_mode = False

app = Flask(__name__, template_folder='monitor_engine/graphic_interface/templates',
            static_folder='monitor_engine/graphic_interface/static')
api = Api(app)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    stacktrace = logging.getLogger('werkzeug')
    stacktrace.disabled = True

    if replay_mode:
        sim_args = {'simulation_config': None, 'to_record': None, 'replay_file_name': replay}

    else:
        while True:
            try:
                response = requests.get(f'http://{base_url}:{api_port}/sim_config').json()
                sim_args = {'simulation_config': response, 'to_record': record}
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

    Logger.normal(f'Graphic Interface: Serving on http://{base_url}:{monitor_port}')
    run_simple(application=app, hostname=base_url, port=int(monitor_port), use_debugger=False)
