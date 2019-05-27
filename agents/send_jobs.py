import requests


def get_action(token, act, param):
    return {"token": token, "action": act, "parameters": param}


token_car = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiY2FyIn0.7son9oUUuWMMG7rvYElgZmZE0U9c88S3eUkQJzSTU5k"
token_drone = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiZHJvbmUifQ.KHIBr07RPIYelWUhpfFBamtQRH23oMykJvqoyHykmu8"
token_boat = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiYm9hdCJ9.a-YWipO-RqEXvTbxwvCLEnz4Z8K8wv4V4M0rNCxCadQ"


car_actions = [get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "photograph", []),
               get_action(token_car, "analyze_photo", []),
               get_action(token_car, "rescue_victim", []),
               get_action(token_car, "rescue_victim", []),
               get_action(token_car, "deliver_physical", ["victim", 2]),
               get_action(token_car, "collect_water", []),
               get_action(token_car, "collect_water", []),
               get_action(token_car, "deliver_physical", ["water_sample", 2])]

drone_actions = [get_action(token_drone, "water_sample", []),
                 get_action(token_drone, "water_sample", []),
                 get_action(token_drone, "photograph", []),
                 get_action(token_drone, "analyze_photo", []),
                 get_action(token_drone, "rescue_victim", []),
                 get_action(token_drone, "deliver_physical", ["water_sample", 2]),
                 get_action(token_drone, "deliver_physical", ["victim", 1]),
                 get_action(token_drone, "search_social_asset", ["doctor"]),
                 get_action(token_drone, "get_social_asset", []),
                 get_action(token_drone, "photograph", [])]

boat_actions = [get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "deliver_physical", ["victim", 2]),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "rescue_victim", []),
                get_action(token_boat, "photograph", []),
                get_action(token_boat, "deliver_physical", ["victim", 2]),
                get_action(token_boat, "photograph", []),
                get_action(token_boat, "deliver_virtual", ["photo", 2]),
                get_action(token_boat, "collect_water", [])]


if __name__ == '__main__':
    steps = 10
    agents = [{'token': token_car, 'name': "car", 'jobs': car_actions},
              {'token': token_drone, 'name': "drone", 'jobs': drone_actions},
              {'token': token_boat, 'name': "boat", 'jobs': boat_actions}]

    for step in range(steps):

        print("-"*20, "Step ", step, "-"*20)

        response = requests.post('http://localhost:8910/send_job', json=car_actions[step]).json()
        print(agents[0]['name'], "  |   send_job = ", response['job_delivered'])

        response = requests.post('http://localhost:8910/send_job', json=drone_actions[step]).json()
        print(agents[1]['name'], "|   send_job = ", response['job_delivered'])

        response = requests.post('http://localhost:8910/send_job', json=boat_actions[step]).json()
        print(agents[2]['name'], " |   send_job = ", response['job_delivered'])

        requests.get('http://localhost:8910/time_ended')

        response = requests.post('http://localhost:8910/get_job', json=token_car).json()
        info = response['simulation_state']['action_results']
        print(agents[0]['name'], "  |   get_job    :  last_action  =   ", info['last_action'],
              "    |  last_action_result", info['last_action_result'])

        response = requests.post('http://localhost:8910/get_job', json=token_drone).json()

        info = response['simulation_state']['action_results']
        print(agents[1]['name'], "|   get_job    :  last_action  =   ", info['last_action'],
              "    |  last_action_result", info['last_action_result'])

        response = requests.post('http://localhost:8910/get_job', json=token_boat).json()
        info = response['simulation_state']['action_results']
        print(agents[2]['name'], " |   get_job    :  last_action  =   ", info['last_action'],
              "    |  last_action_result", info['last_action_result'])







