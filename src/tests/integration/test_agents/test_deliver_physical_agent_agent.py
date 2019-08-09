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
water_loc = None
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


def get_water_loc(msg):
    my_location = [msg['agent']['location']['lat'], msg['agent']['location']['lon']]
    min_distance = 999999999
    water_location = None
    for event in msg['environment']['events']:
        if event['type'] == 'water_sample':
            actual_distance = calculate_distance(my_location, [event['location']['lat'], event['location']['lon']])
            if actual_distance < min_distance:
                min_distance = actual_distance
                water_location = [event['location']['lat'], event['location']['lon']]

    return water_location


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@delivering_socket.on('action_results')
def delivering_action_results(msg):
    global collected, water_loc
    msg = json.loads(msg)

    responses.append(msg['agent']['last_action_result'])

    if msg['environment']['step'] == 1:
        water_loc = get_water_loc(msg)
        requests.post('http://127.0.0.1:12345/send_action',
                      json=json.dumps({'token': delivering_token, 'action': 'move', 'parameters': water_loc}))

    elif msg['agent']['last_action'] == 'deliverPhysical':
        delivering_socket.emit('disconnect_registered_agent', data=json.dumps({'token': delivering_token}), callback=quit_program)

    elif not msg['agent']['route']:
        if msg['agent']['last_action'] == 'collectWater':
            collected = True
            delivering_socket.emit('send_action', json.dumps({'token': delivering_token, 'action': 'move', 'parameters': delivery_location}))

        elif not collected:
            delivering_socket.emit('send_action', json.dumps({'token': delivering_token,
                                                              'action': 'collectWater', 'parameters': []}))

        elif msg['agent']['last_action'] == 'move':
            delivering_socket.emit('send_action', json.dumps({'token': delivering_token, 'action': 'deliverPhysical',
                                                              'parameters': ['water_sample', 1, receiving_token]}))

    else:
        delivering_socket.emit('send_action', json.dumps({'token': delivering_token, 'action': 'move', 'parameters': water_loc}))


@receiving_socket.on('action_results')
def receiving_action_results(msg):
    global delivery_location
    msg = json.loads(msg)

    if msg['environment']['step'] == 1:
        delivery_location = msg['agent']['location']
        receiving_socket.emit('send_action', json.dumps({'token': receiving_token, 'action': 'pass', 'parameters': []}))

    elif msg['agent']['last_action_result'] and msg['agent']['last_action'] == 'receivePhysical':
        responses.append(True)
        receiving_socket.emit('disconnect_registered_agent', json.dumps({'token': receiving_token}), callback=quit_program)

    else:
        receiving_socket.emit('send_action', json.dumps({'token': receiving_token, 'action': 'receivePhysical', 'parameters': [delivering_token]}))


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