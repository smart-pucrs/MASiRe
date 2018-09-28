from flask_socketio import emit


def response_to_action_ready(response, token):
    emit(token, response, callback=ack)


def response_to_action_deliver(event, response):
    emit(event, response)


def response_to_action_connect(event, response):
    emit(event, response)


def ack():
    print('message was received!')
