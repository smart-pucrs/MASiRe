import requests
import json


def get_action(token, act, param):
    return {"token": token, "action": act, "parameters": param}


token_car = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQxIn0.OyDxesy_GlKAZxdaGieiUVas-W6BCpVVzNQMwU3cd9s"
token_drone = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQyIn0.ocVROx0f1A7fH8fq9x8WRMNITSDi7q-HtGT0lAUhMPg"
token_boat = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQzIn0.7EDzzHgxbuLOa5oncQdMrIJ7ceIi_GbHDWY97NEiNs4"
steps = 5

car_actions = [get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "analyze_photo", []),
               get_action(token_car, "rescue_victim", [])]


def do_actions():
    actions = []

    for action in car_actions:
        actions.append(action)
        response = requests.post('http://localhost:12345/do_actions', json=actions).json()

        print("Car: ", json.dumps(response, indent=4, sort_keys=False))


if __name__ == '__main__':
    do_actions()
