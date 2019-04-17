import requests

agent = {
    "name": "ubuntu",
}


if __name__ == '__main__':
    response = requests.post('http://localhost:12345/connect_agent', json=agent).json()
    print(response)
    agent['token'] = response['data']

    action = {
        "token": agent['token'],
        "action": "move",
        "parameters": [-30.109611, -51.211556]
    }

    response = requests.post('http://localhost:12345/validate_agent', json=agent['token']).json()
    print(response)
    agent = response

    response = requests.post('http://localhost:12345/job', json=action).json()
    print(response)






