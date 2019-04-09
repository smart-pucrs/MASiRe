from flask import Flask
from flask_cors import CORS
from src.communication import listeners


if __name__ == '__main__':
    socketio = listeners.socketio
    app = Flask(__name__)
    app.debug = False
    CORS(app)
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    socketio.init_app(app)
    socketio.run(app)
