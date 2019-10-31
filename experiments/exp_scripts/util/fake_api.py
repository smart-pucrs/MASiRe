import sys
from flask_socketio import SocketIO
from flask import Flask, request, jsonify

base_url, api_port, secret = sys.argv[1:]

app = Flask(__name__)
socket = SocketIO(app=app)


@app.route('/start_connections', methods=['POST'])
def start_connections():
    socket.emit('sim_started', '')

    return jsonify('')


if __name__ == '__main__':
    app.config['SECRET_KEY'] = secret
    app.config['JSON_SORT_KEYS'] = False
    print(f'API: Serving on http://{base_url}:{api_port}')
    socket.run(app=app, host=base_url, port=api_port)
