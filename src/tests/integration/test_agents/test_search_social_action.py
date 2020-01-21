import requests
import json
import socketio


agent = {'name': 'search_action_test'}
fake = {'name': 'fake'}
wait = True
responses = []


socket = socketio.Client()
fake_socket = socketio.Client()
token = None
fake_token = None


def connect_agent():
    global token, fake_token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
    token = response['message']
    socket.emit('register_agent', data={'token': token})

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=fake).json()
    fake_token = response['message']
    fake_socket.emit('register_agent', data={'token': fake_token})


@fake_socket.on('percepts')
def pass_action(msg):
    socket.emit('send_action', data=json.dumps({'token': fake_token, 'action': 'pass', 'parameters': []}))


@socket.on('percepts')
def action_result(msg):
    msg = json.loads(msg)
    responses.append(msg['agent']['last_action_result'] == 'success')

    if msg['environment']['step'] == 1:
        socket.emit('send_action', data=json.dumps({'token': token, 'action': 'searchSocialAsset', 'parameters': [1000]}))

    else:
        socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)


@socket.on('simulation_ended')
def simulation_ended(*args):
    global wait
    wait = False


def quit_program(*args):
    global wait
    wait = False


def test_cycle():
    socket.connect('http://127.0.0.1:12345')
    fake_socket.connect('http://127.0.0.1:12345')
    connect_agent()
    while wait:
        pass

    socket.disconnect()
    fake_socket.disconnect()
    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)
