import requests

port = 8910
agents = [
            {
                "name": "car"
            },
            {
                "name": "drone"
            },
            {
                "name": "boat"
            }
        ]

if __name__ == '__main__':
    for agent in agents:
        response = requests.post('http://127.0.0.1:12345/connect_agent', json=agent).json()
        agent['token'] = response['data']

    for agent in agents:
        response = requests.post('http://127.0.0.1:12345/validate_agent', json=agent['token']).json()
        print(agent['name'], " conectado!")







