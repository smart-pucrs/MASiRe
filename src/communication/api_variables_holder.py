from flask_socketio import SocketIO
from flask import Blueprint

variables = {}


def initialize_all():
    variables['socketio'] = SocketIO()
    variables['main'] = Blueprint('main', __name__)

    # Load the decorators for the socketio and blueprint objects
    from src.communication.routes import routes
    from src.communication.events import listeners
