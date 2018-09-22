from flask_socketio import emit


def response_to_action(response, token):
    emit(token, response, callback=ack)


def ack():
    print('message was received!')

