import requests
import json
import socketio


agent = {'name': 'water_action_test'}
wait = True
responses = []


socket = socketio.Client()
token = None
water_loc = None


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


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


@socket.on('action_results')
def action_result(msg):
    global water_loc
    print(msg)
    msg = json.loads(msg)
    responses.append(msg['agent']['last_action_result'])

    if msg['environment']['step'] == 1:
        water_loc = get_water_loc(msg)
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': water_loc}))

    elif not msg['agent']['route']:
        if msg['agent']['last_action'] == 'collectWater':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        else:
            socket.emit('send_action', json.dumps({'token': token, 'action': 'collectWater', 'parameters': []}))

    else:
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': water_loc}))


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

