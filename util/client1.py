from flask import Flask, render_template
import socketio
import requests

app = Flask(__name__)
socket = socketio.Client()


@app.route("/")
def home():
    return render_template("index.html")


@socket.on('connect')
def connect():
    print('Connected!')


if __name__ == "__main__":
    socket.connect('http://127.0.0.1:12345')
    app.run(debug=True)
