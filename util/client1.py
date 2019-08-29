import json
import requests
import socketio

client1 = socketio.Client()
client2 = socketio.Client()
client1.connect('http://127.0.0.1:12345')
client2.connect('http://127.0.0.1:12345')
