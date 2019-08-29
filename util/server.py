import json
import requests
import socketio
from flask_socketio import SocketIO
from flask import Flask

app = Flask(__name__)
server = SocketIO(app)


@server.on('connect')
def connect():
    print('Connected!')


if __name__ == '__main__':
    server.run(app=app, host='127.0.0.1', port=12345)

