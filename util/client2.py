import json
import requests
import socketio

client = socketio.Client()
client.connect('http://127.0.0.1:12345')
