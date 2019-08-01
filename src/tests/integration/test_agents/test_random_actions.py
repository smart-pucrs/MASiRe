import requests
import json
import socketio
import random


agent = {'name': 'random_action_test'}
actions = ['move', 'pass', 'rescueVictim', 'takePhoto', 'analyzePhoto', 'collectWater',
           'deliverPhysical', 'deliverVirtual', 'searchSocialAsset', 'carry', 'getCarried', 'charge']
wait = True
responses = []

socket = socketio.Client()
token = None


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


@socket.on('simulation_started')
def simulation_started(msg):
    action = random.choice(actions)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': action, 'parameters': []}))


@socket.on('action_results')
def action_result(msg):
    try:
        action = random.choice(actions)
        requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': action, 'parameters': []}))
        responses.append(True)

    except:
        responses.append(False)


@socket.on('simulation_ended')
def simulation_ended(*args):
    global wait
    wait = False


def quit_program(*args):
    global wait
    wait = False


def test_cycle():
    socket.connect('http://127.0.0.1:12345')
    connect_agent()
    while wait:
        pass

    socket.disconnect()
    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)
