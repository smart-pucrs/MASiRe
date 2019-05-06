import requests
import json

token_car = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQxIn0.OyDxesy_GlKAZxdaGieiUVas-W6BCpVVzNQMwU3cd9s"
token_drone = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQyIn0.ocVROx0f1A7fH8fq9x8WRMNITSDi7q-HtGT0lAUhMPg"
token_boat = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYWdlbnQzIn0.7EDzzHgxbuLOa5oncQdMrIJ7ceIi_GbHDWY97NEiNs4"

if __name__ == '__main__':

    actions = [{
                    "token": token_car,
                    "action": "move",
                    "parameters": [-30.109611, -51.211556]
                },
                {
                    "token": token_drone,
                    "action": "photograph",
                    "parameters": []
                },
                {
                    "token": token_boat,
                    "action": "collect_water",
                    "parameters": []
                }]

    response = requests.post('http://localhost:12345/do_actions', json=actions).json()

    json_string_car = response['action_results'][0][1]
    json_string_drone = response['action_results'][1][1]
    json_string_boat = response['action_results'][2][1]

    print("Car: ", json.dumps(json_string_car, indent=4, sort_keys=False))
    print("Drone: ", json.dumps(json_string_drone, indent=4, sort_keys=False))
    print("Boat: ", json.dumps(json_string_boat, indent=4, sort_keys=False))





