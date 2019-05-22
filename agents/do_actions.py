import requests
import json


def get_action(token, act, param):
    return {"token": token, "action": act, "parameters": param}


token_car = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQxIn0.OyDxesy_GlKAZxdaGieiUVas-W6BCpVVzNQMwU3cd9s"
token_drone = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQyIn0.ocVROx0f1A7fH8fq9x8WRMNITSDi7q-HtGT0lAUhMPg"
token_boat = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQzIn0.7EDzzHgxbuLOa5oncQdMrIJ7ceIi_GbHDWY97NEiNs4"
steps = 10

car_actions = [get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "analyze_photo", []),
               get_action(token_car, "rescue_victim", []),
               get_action(token_car, "rescue_victim", []),
               get_action(token_car, "deliver_physical", ["victim", 2]),
               get_action(token_car, "collect_water", []),
               get_action(token_car, "collect_water", [])]

drone_actions = [get_action(token_drone, "water_sample", []),
                 get_action(token_drone, "water_sample", []),
                 get_action(token_drone, "photograph", []),
                 get_action(token_drone, "analyze_photo", []),
                 get_action(token_drone, "rescue_victim", []),
                 get_action(token_drone, "deliver_physical", ["water_sample", 2]),
                 get_action(token_drone, "deliver_physical", ["victim", 1]),
                 get_action(token_drone, "search_social_asset", ["doctor"]),
                 get_action(token_drone, "get_social_asset", [])]

boat_actions = [get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "deliver_physical", ["victim", 2]),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "photograph", []),
                get_action(token_boat, "deliver_physical", ["victim", 2]),
                get_action(token_boat, "photograph", []),
                get_action(token_boat, "deliver_virtual", ["photo", 2])]


def do_actions():
    actions = []
    agents = ["car", "drone", "boat"]
    steps = 10

    for step in range(steps-1):
        actions.append(car_actions[step])
        actions.append(drone_actions[step])
        actions.append(boat_actions[step])

        print("Resultado do Step ", step+1, ":")
        response = requests.post('http://localhost:8910/do_actions', json=actions).json()
        actions = []

        for agent in range(3):
            info = response['action_results'][agent][1]
            print(agents[agent], " : ", info['last_action'], " : ", info['last_action_result'])


if __name__ == '__main__':
    do_actions()
