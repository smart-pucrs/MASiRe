import jwt
from flask import request, jsonify, json
from src.communication import main


@main.route('/list')
def list_agents():
    f = open('agents.json', 'r').read()
    json_string = f.rstrip()
    available_agents = json.loads(json_string)

    return jsonify(available_agents)


@main.route('/requestConnection', methods=['POST'])
def connect():
    agent = request.get_json()
    print(agent)
    encoded = jwt.encode(agent, 'secret', algorithm='HS256')
    response = {
        "encoded": encoded.decode('utf-8'),
        "ip": '127.0.0.1',
        "port": 5000
    }
    return jsonify(response)
