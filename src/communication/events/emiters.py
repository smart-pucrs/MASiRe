from flask_socketio import emit


def response_to_action(response, token):
    emit(token+'/action_respone', response, callback=ack)


def emit_pre_step(pre_step, token):
    emit(token+'/pre_step', pre_step, callback=ack)


def ack():
    print('message was received!')
