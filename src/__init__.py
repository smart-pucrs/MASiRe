import sys

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from src.manager import SimulationInstance

socketio = SocketIO()


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    CORS(app)
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    SimulationInstance.get_instance('config.json')

    from .communication import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    return app

