import requests
import json
import socketio


agent = {'name': 'analyze_action_test'}
agent_pass_action = {'name': 'pass_action'}
wait = True
responses = []


socket = socketio.Client()
pass_action_socket = socketio.Client()
token = None
token_pass_action = None
photo_loc = []


def connect_agents():
    global token, token_pass_action

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
    token = response['message']
    socket.emit('register_agent', data={'token': token})

    response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent_pass_action).json()
    token_pass_action = response['message']
    pass_action_socket.emit('register_agent', data={'token': token_pass_action})


def get_photo_loc(msg):
    my_location = [msg['agent']['location']['lat'], msg['agent']['location']['lon']]
    min_distance = 999999999
    photo_loc = None
    for event in msg['environment']['events']:
        if event['type'] == 'photo':
            actual_distance = calculate_distance(my_location, [event['location']['lat'], event['location']['lon']])
            if actual_distance < min_distance:
                min_distance = actual_distance
                photo_loc = [event['location']['lat'], event['location']['lon']]

    return photo_loc


def calculate_distance(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5


@pass_action_socket.on('percepts')
def pass_action(result):
    pass_action_socket.emit('send_action', json.dumps({'token': token_pass_action, 'action': 'pass', 'parameters': []}))


@socket.on('percepts')
def action_result(result):
    global photo_loc
    msg = json.loads(result)
    responses.append(msg['agent']['last_action_result'] == 'success')
    if msg['environment']['step'] == 1:
        photo_loc = get_photo_loc(msg)
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': photo_loc}))

    elif not msg['agent']['route']:
        if msg['agent']['last_action'] == 'takePhoto':
            socket.emit('send_action', json.dumps({'token': token, 'action': 'analyzePhoto', 'parameters': []}))

        elif msg['agent']['last_action'] == 'analyzePhoto':
            socket.emit('disconnect_registered_agent', data=json.dumps({'token': token}), callback=quit_program)

        else:
            socket.emit('send_action', json.dumps({'token': token, 'action': 'takePhoto', 'parameters': []}))

    else:
        socket.emit('send_action', json.dumps({'token': token, 'action': 'move', 'parameters': photo_loc}))


@socket.on('simulation_ended')
def simulation_ended(*args):
    global wait
    wait = False


def quit_program(*args):
    global wait
    wait = False


def test_cycle():
    socket.connect('http://127.0.0.1:12345')
    pass_action_socket.connect('http://127.0.0.1:12345')
    connect_agents()

    while wait:
        pass

    socket.disconnect()
    pass_action_socket.disconnect()

    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)
