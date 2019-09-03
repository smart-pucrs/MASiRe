from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
server = SocketIO(app)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    server.run(app=app, host='127.0.0.1', port=8000)
