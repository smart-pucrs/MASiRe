import json
import requests
import socketio

socket = socketio.Client()
socket.connect('http://127.0.0.1:12345')

info = {'main_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiY29ubmVjdGlvbkExIn0.7ltKanLv9douhqaBCFdp47teHalaoeMo9wB6svBgvOo',
        'step': 6,
        'agent_info': {'name': 'social_asset'}}

response = requests.post('http://127.0.0.1:12345/connect_asset', json=json.dumps(info)).json()
print(response)
delivering_token = response['message']
requests.post('http://127.0.0.1:12345/register_asset', json=json.dumps({'token': delivering_token}))
socket.emit('connect_registered_asset', data=json.dumps({'token': delivering_token}))
socket.emit('join', {'room': 'social_asset'})


@socket.on('initial_percepts')
def social_asset(msg):
    print('[Initial_percepts]: ', msg)


@socket.on('action_results')
def percepts(msg):
    print('[action_results]: ', msg)
    socket.emit('send_action', data=json.dumps({'token': delivering_token, 'action': 'pass', 'parameters': []}))


@socket.on('social_asset')
def percepts(msg):
    print('[social_asset]: ', msg)
    socket.emit('send_action', data=json.dumps({'token': delivering_token, 'action': 'pass', 'parameters': []}))
