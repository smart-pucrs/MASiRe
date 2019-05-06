import requests

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
        response = requests.post('http://localhost:8910/connect_agent', json=agent).json()
        agent['token'] = response['data']

    for agent in agents:
        response = requests.post('http://localhost:8910/validate_agent', json=agent['token']).json()
        print(agent['name'], " conectado!")







