import requests
import json
import socketio


agent = {'name': 'virtual_action_test'}
wait = True
responses = []


socket = socketio.Client()
token = None
got = False


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


@socket.on('simulation_started')
def simulation_started(msg):
    photo_loc = get_photo_loc(msg)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'move', 'parameters': photo_loc}))


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


@socket.on('action_results')
def action_result(msg):
    global got

    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'])

    if not msg['agent']['route']:
        if msg['agent']['last_action'] == 'deliverVirtual':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        elif not got:
            got = True
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'takePhoto', 'parameters': []}))

        elif got and msg['agent']['last_action'] == 'move':
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'deliverVirtual', 'parameters': ['photo']}))

        elif got:
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'move', 'parameters': ['cdm']}))

    else:
        requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'move', 'parameters': []}))


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
