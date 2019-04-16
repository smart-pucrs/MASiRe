import requests
import multiprocessing
from flask import Flask, request


app = Flask(__name__)

agent = {
    "name": "ubuntu",
    "url": "http://localhost:45678/ubuntu"
}

action = {
    "token": agent['token'],
    "action": "move",
    "parameters": [-30.109611, -51.211556]
}


@app.route(agent['url'])
def listen():
    results = request.get_json()
    print(results)


def start_app():
    app.run(port=45678)


if __name__ == '__main__':
    aux = multiprocessing.Process(target=start_app)
    aux.start()

    response = requests.post('http://localhost:12345/connect_agent', json=agent).json()
    print(response)
    agent['token'] = response['data']

    response = requests.post('http://localhost:12345/validate_agent', json=agent['token']).json()
    print(response)
    agent = response

    response = requests.post('http://localhost:12345/job', json=action).json()
    print(response)

    aux.join()





