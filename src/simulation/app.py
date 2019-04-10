import json
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS
from src.simulation.simulation import Simulation


def start_instance(path):
    with open(path, 'r') as simulation_config:
        json_config = json.loads(simulation_config.read())
        return Simulation(json_config)


app = Flask(__name__)
simulation = start_instance('files/config.json')
simulation.start()


@app.route('/register_agent', methods=['POST'])
def register_agent():
    token = request.get_json()
    if token is not None:
        result = simulation.create_agent(token)
        return jsonify(result.__dict__)
    return 'NoneType'


@app.route('/do_action', methods=['POST'])
def do_actions():
    actions = request.get_json()
    if actions is not None:
        result = simulation.do_step(actions)
        return jsonify(result)
    return 'NoneType'


if __name__ == '__main__':
    app.debug = False
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    CORS(app)
    app.run(port='50000')
