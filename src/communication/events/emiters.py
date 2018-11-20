from flask_socketio import emit


def on_response(event, response):
    print(event)
    emit(event, response)


def response_to_action_connect():
    pass

def emit_pre_step():
    pass