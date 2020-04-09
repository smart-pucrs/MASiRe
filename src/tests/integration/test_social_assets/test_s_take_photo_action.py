import requests
import json
import socketio


asset = {'name': 'photo_action_test'}
wait = True
responses = []


socket = socketio.Client()
token = None


def connect_asset():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_asset', json=json.dumps(asset)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_asset', json=json.dumps({'token': token}))
    socket.emit('connect_registered_asset', data=json.dumps({'token': token}))


@socket.on('simulation_started')
def simulation_started(msg):
    photo_loc = get_photo_loc(msg)
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'move', 'parameters': photo_loc}))


def get_photo_loc(msg):
    msg = json.loads(msg)
    my_location = msg['social_asset']['location']
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
    msg = json.loads(msg)

    if msg['message'] == 'Asset is not capable of entering flood locations.':
        responses.append(True)
        socket.emit('disconnect_registered_asset', data=json.dumps({'token': token}), callback=quit_program)
        return

    responses.append(msg['social_asset']['last_action_result'])

    if not msg['social_asset']['route']:
        if msg['social_asset']['last_action'] == 'takePhoto':
            socket.emit('disconnect_registered_asset', data=json.dumps({'token': token}), callback=quit_program)

        else:
            requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'takePhoto', 'parameters': []}))

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
    connect_asset()
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