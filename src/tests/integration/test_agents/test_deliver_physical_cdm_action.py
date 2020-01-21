import requests
import json
import socketio


agent = {'name': 'physical_action_test'}
fake = {'name': 'fake'}
wait = True
responses = []


socket = socketio.Client()
fake_socket = socketio.Client()
token = None
fake_token = None
got = False
water_loc = None


def connect_agent():
    global token, fake_token

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
    token = response['message']
    socket.emit('register_agent', data={'token': token})

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=fake).json()
    fake_token = response['message']
    fake_socket.emit('register_agent', data={'token': fake_token})


def get_water_loc(msg):
    my_location = [msg['agent']['location']['lat'], msg['agent']['location']['lon']]
    min_distance = 999999999
    location = None
    for event in msg['environment']['events']:
        if event['type'] == 'water_sample':
            actual_distance = calculate_distance(my_location, [event['location']['lat'], event['location']['lon']])
            if actual_distance < min_distance:
                min_distance = actual_distance
                location = [event['location']['lat'], event['location']['lon']]

    return location


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@fake_socket.on('percepts')
def pass_action(msg):
    fake_socket.emit('send_action', data=json.dumps({'token': fake_token, 'action': 'pass', 'parameters': []}))


@socket.on('percepts')
def action_result(msg):
    global got, water_loc

    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'] == 'success')

    if msg['environment']['step'] == 1:
        water_loc = get_water_loc(msg)
        socket.emit('send_action', data=json.dumps({'token': token, 'action': 'move', 'parameters': water_loc}))

    elif not msg['agent']['route']:
        if msg['agent']['last_action'] == 'deliverPhysical':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        elif not got:
            got = True
            socket.emit('send_action', data=json.dumps({'token': token, 'action': 'collectWater', 'parameters': []}))

        elif got and msg['agent']['last_action'] == 'move':
            socket.emit('send_action', data=json.dumps({'token': token, 'action': 'deliverPhysical', 'parameters': ['water_sample']}))

        elif got:
            socket.emit('send_action', data=json.dumps({'token': token, 'action': 'move', 'parameters': ['cdm']}))

    else:
        if msg['agent']['physical_storage_vector']:
            socket.emit('send_action', data=json.dumps({'token': token, 'action': 'move', 'parameters': ['cdm']}))
        else:
            socket.emit('send_action', data=json.dumps({'token': token, 'action': 'move', 'parameters': water_loc}))


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

