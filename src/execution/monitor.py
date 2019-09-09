import sys
import socketio
import random
import time

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO

monitor_url, monitor_port, secret = sys.argv[1:]
app = Flask(__name__)
socket = socketio.Client()

simulation_steps = []


@socket.on('monitor')
def monitor(data):
    print('[ MONITOR ][ NORMAL ] ## Data Received!')

    simulation_steps.append(data)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/refresh', methods=['GET'])
def refresh():
    global simulation_steps

    data = None
    if simulation_steps:
        data = simulation_steps.pop(0)

    return jsonify(data)

@app.route('/victim_icon', methods=['GET'])
def victim_icon():
    return send_file('templates/images/victim_icon.png')


@app.route('/flood_icon', methods=['GET'])
def flood_icon():
    return send_file('templates/images/flood_icon.png')


@app.route('/water_sample_icon', methods=['GET'])
def water_sample_icon():
    return send_file('templates/images/water_sample_icon.png')


@app.route('/photo_icon', methods=['GET'])
def photo_icon():
    return send_file('templates/images/photo_icon.png')


@app.route('/agent_icon', methods=['GET'])
def agent_icon():
    return send_file('templates/images/agent_icon.png')


if __name__ == "__main__":
    time.sleep(.5)
    socket.connect('http://127.0.0.1:12345')
    app.run(host='127.0.0.1', port=8000)
