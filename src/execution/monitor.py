import sys

from flask import Flask, render_template
from flask_socketio import SocketIO

monitor_url, monitor_port, secret = sys.argv[1:]
app = Flask(__name__)
server = SocketIO(app)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    server.run(app=app, host=monitor_url, port=int(monitor_port))
