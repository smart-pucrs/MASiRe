import requests
import json
import socketio


agent = {'name': 'pass_action_test'}
wait = True
responses = []


socket = socketio.Client()
token = None
counter = 0
max_iter = 16


def connect_agent():
    global token
    response = requests.post('http://127.0.0.1:12345/connect_agent', json=json.dumps(agent)).json()
    token = response['message']
    requests.post('http://127.0.0.1:12345/register_agent', json=json.dumps({'token': token}))
    socket.emit('connect_registered_agent', data=json.dumps({'token': token}))


@socket.on('action_results')
def action_result(msg):
    global counter
    msg = json.loads(msg)

    if msg['environment']['step'] == 1:
        socket.emit('send_action', json.dumps({'token': token, 'action': 'pass', 'parameters': []}))
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
