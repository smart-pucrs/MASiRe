from flask import Flask
from flask_cors import CORS
from src.communication import api_variables_holder


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    CORS(app)
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    app.register_blueprint(main)

    socketio.init_app(app)
    socketio.run(app)


if __name__ == '__main__':
    api_variables_holder.initialize_all()
    socketio = api_variables_holder.variables['socketio']
    main = api_variables_holder.variables['main']
    create_app(debug=True)
