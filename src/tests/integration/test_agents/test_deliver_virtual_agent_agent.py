import json
import requests
import socketio


delivering_agent = {'name': 'delivering_agent'}
receiving_agent = {'name': 'receiving_agent'}


delivering_socket = socketio.Client()
receiving_socket = socketio.Client()

waits = []
responses = []

delivering_token = None
receiving_token = None

delivery_location = None
collected = False


def connect_actors():
    global delivering_token, receiving_token

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(delivering_agent)).json()
    delivering_token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': delivering_token}))
    delivering_socket.emit('connect_registered_agent', data=json.dumps({'token': delivering_token}))

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(receiving_agent)).json()
    receiving_token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': receiving_token}))
    receiving_socket.emit('connect_registered_agent', data=json.dumps({'token': receiving_token}))


@delivering_socket.on('simulation_started')
def delivering_simulation_started(msg):
    photo_loc = get_photo_loc(msg)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': delivering_token, 'action': 'move', 'parameters': photo_loc}))


def get_photo_loc(msg):
    msg = json.loads(msg)
    my_location = msg['agent']['location']
    min_distance = 999999999
    photo_loc = None
    for photo in msg['event']['photos']:
        actual_distance = calculate_distance(my_location, photo['location'])
        if actual_distance < min_distance:
            min_distance = actual_distance
            photo_loc = photo['location']

    return photo_loc


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@receiving_socket.on('simulation_started')
def receiving_simulation_started(msg):
    global delivery_location

    msg = json.loads(msg)
    delivery_location = msg['agent']['location']
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': receiving_token, 'action': 'pass', 'parameters': []}))


@delivering_socket.on('action_results')
def delivering_action_results(msg):
    global collected
    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'])

    if msg['agent']['last_action'] == 'deliverVirtual':
        delivering_socket.emit('disconnect_registered_agent', data=json.dumps({'token': delivering_token}), callback=quit_program)

    if not msg['agent']['route']:
        if msg['agent']['last_action'] == 'takePhoto':
            collected = True
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': delivering_token, 'action': 'move', 'parameters': delivery_location}))

        elif not collected:
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': delivering_token, 'action': 'takePhoto', 'parameters': []}))

        elif msg['agent']['last_action'] == 'move':
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': delivering_token, 'action': 'deliverVirtual', 'parameters': ['photo', 1, receiving_token]}))

    else:
        requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': delivering_token, 'action': 'move', 'parameters': []}))


@receiving_socket.on('action_results')
def receiving_action_results(msg):
    msg = json.loads(msg)

    if msg['agent']['last_action_result'] and msg['agent']['last_action'] == 'receiveVirtual':
        responses.append(True)
        receiving_socket.emit('disconnect_registered_agent', data=json.dumps({'token': receiving_token}), callback=quit_program)

    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': receiving_token, 'action': 'receiveVirtual', 'parameters': [delivering_token]}))


def quit_program(msg):
    waits.append(True)


def test_cycle():
    delivering_socket.connect('http://127.0.0.1:12345')
    receiving_socket.connect('http://127.0.0.1:12345')
    connect_actors()
    while len(waits) < 2:
        pass

    delivering_socket.disconnect()
    receiving_socket.disconnect()

    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)