import json
import requests
import socketio


agent = {'name': 'carrying_agent'}
carried_agent = {'name': 'carried_agent'}

waits = []
responses = []


carrying_socket = socketio.Client()
carried_socket = socketio.Client()
token = None
carried_token = None


def connect_actors():
    global token, carried_token

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
    token = response['message']
    carrying_socket.emit('register_agent', data={'token': token})

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=carried_agent).json()
    carried_token = response['message']
    carried_socket.emit('register_agent', data={'token': carried_token})


@carrying_socket.on('percepts')
def carry_action_results(msg):
    msg = json.loads(msg)

    if msg['environment']['step'] == 1:
        carrying_socket.emit('send_action', json.dumps({'token': token, 'action': 'carry', 'parameters': [carried_token]}))

    else:
        responses.append(msg['agent']['last_action_result'] == 'success')
        carrying_socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)


@carried_socket.on('percepts')
def carried_action_results(msg):
    msg = json.loads(msg)

    if msg['environment']['step'] == 1:
        carried_socket.emit('send_action',
                            json.dumps({'token': carried_token, 'action': 'getCarried', 'parameters': [token]}))

    else:
        responses.append(msg['agent']['last_action_result'] == 'success')
        carried_socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)


def quit_program(*args):
    waits.append(True)


def test_cycle():
    carrying_socket.connect('http://127.0.0.1:12345')
    carried_socket.connect('http://127.0.0.1:12345')
    connect_actors()
    while len(waits) < 2:
        pass

    carrying_socket.disconnect()
    carried_socket.disconnect()

    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)
