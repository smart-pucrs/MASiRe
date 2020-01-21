import requests
import json
import socketio


agent = {'name': 'move_action_test'}
fake = {'name': 'fake'}
wait = True
responses = []

socket = socketio.Client()
fake_socket = socketio.Client()
token = None
fake_token = None
farther_obj = None


def connect_agent():
    global token, fake_token

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
    token = response['message']
    socket.emit('register_agent', data={'token': token})

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=fake).json()
    fake_token = response['message']
    fake_socket.emit('register_agent', data={'token': fake_token})


def get_farther_loc(msg):
    my_location = [msg['agent']['location']['lat'], msg['agent']['location']['lon']]
    max_distance = 0
    obj_loc = None
    for event in msg['environment']['events']:
        if event['type'] != 'flood':
            actual_distance = calculate_distance([event['location']['lat'], event['location']['lon']], my_location)
            if actual_distance > max_distance:
                max_distance = actual_distance
                obj_loc = [event['location']['lat'], event['location']['lon']]

    return obj_loc


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@fake_socket.on('percepts')
def pass_action(msg):
    fake_socket.emit('send_action', data=json.dumps({'token': fake_token, 'action': 'pass', 'parameters': []}))


@socket.on('percepts')
def action_result(msg):
    global farther_obj
    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'] == 'success')
    if msg['environment']['step'] == 1:
        farther_obj = get_farther_loc(msg)
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': farther_obj}))

    elif not msg['agent']['route']:
        socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)
    else:
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': farther_obj}))


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
