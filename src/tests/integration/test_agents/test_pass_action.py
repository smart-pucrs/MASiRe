import requests
import json
import socketio


agent = {'name': 'pass_action_test'}
fake = {'name': 'fake'}
wait = True
responses = []


socket = socketio.Client()
fake_socket = socketio.Client()
token = None
fake_token = None
counter = 0
max_iter = 16


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
    fake_socket.emit('send_action', data=json.dumps({'token': fake_token, 'action': 'pass', 'parameters': []}))


@socket.on('percepts')
def action_result(msg):
    global counter
    msg = json.loads(msg)

    if counter == max_iter:
        socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)
    else:
        socket.emit('send_action', json.dumps({'token': token, 'action': 'pass', 'parameters': []}))
        counter += 1


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
