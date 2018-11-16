from flask_socketio import emit


def response_to_action_ready(response, token):
    emit(token+'/action_response', response, callback=ack)


def emit_pre_step(pre_step, token):
    emit(token+'/pre_step', pre_step, callback=ack)


def response_to_action_deliver(event, response):
    emit(event, response)


def response_to_action_connect(event, response):
    emit(event, response)


# REVIEW WHY WE HAVE TWO RESPONSE_TO_ACTION_READY
def response_to_action_ready2(response, token):
    emit(token + '/connecting_agents', response, callback=ack)


def response_jobs_result(event, response):
    for r in response:
        emit(event, r)


def ack():
    print('Message was received!')
