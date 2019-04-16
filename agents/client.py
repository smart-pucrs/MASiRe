import requests


agent = {
    "name": "ubuntu",
    "version": "1.3",
    "owner": "87462"
}


agent['url'] = agent['url'] + agent['name']


if __name__ == '__main__':
    response = requests.post('http://localhost:12345/connect_agent', json=agent).json()
    agent['token'] = response['data']
    response = requests.post('http://localhost:12345/validate_agent', json=agent['token']).json()
    print(response)





