import json
import requests
import socketio

client = socketio.Client()
client.connect('http://127.0.0.1:12345')
client.emit('message', '1')
client1 = socketio.Client()
client1.connect('http://127.0.0.1:12345')
client1.emit('message', '2')
client2 = socketio.Client()
client2.connect('http://127.0.0.1:12345')
client2.emit('message', '3')
client3 = socketio.Client()
client3.connect('http://127.0.0.1:12345')
client3.emit('message', '4')
client4 = socketio.Client()
client4.connect('http://127.0.0.1:12345')
client4.emit('message', '5')