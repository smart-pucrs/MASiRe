import requests
import json
import socketio


agent = {'name': 'search_action_test'}
asset = {'name': 'search_action_test2'}
wait = True
responses = []


socket = socketio.Client()
other_socket = socketio.Client()
token = None


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))

    response = requests.post('http://127.0.0.1:12345/connect_asset', json=json.dumps(asset)).json()
    other_token = response['message']
    requests.post('http://127.0.0.1:12345/register_asset', json=json.dumps({'token': other_token}))
    other_socket.emit('connect_registered_asset', data=json.dumps({'token': other_token}))


@socket.on('simulation_started')
def simulation_started(msg):
    requests.post('http://127.0.0.1:12345/send_action', json=json.dumps({'token': token, 'action': 'searchSocialAsset', 'parameters': ['doctor']}))


@socket.on('action_results')
def action_result(msg):
    msg = json.loads(msg)
    responses.append(msg['agent']['last_action_result'])
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
    other_socket.connect('http://127.0.0.1:12345')
    connect_agent()
    while wait:
        pass

    socket.disconnect()
    other_socket.disconnect()
    assert all(responses)


if __name__ == '__main__':
    try:
        test_cycle()
        print(True)
    except AssertionError:
        print(False)
