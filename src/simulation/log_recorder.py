import os
import time
import json
from datetime import datetime
from directory_path import dir as root


class Logger:
    def __init__(self, simulation_id):
        time_of_date = f'{datetime.today().hour}h_{datetime.today().minute}m'
        day = str(datetime.today().strftime("%d"))
        month = str(datetime.today().strftime("%B"))
        year = str(datetime.today().strftime("%Y"))
        self.log_file = root / 'files' / simulation_id / year / month / day
        self.percepts_file = root / 'files' / simulation_id / year / month / day
        self.timer = time.time()

        os.makedirs(self.log_file, exist_ok=True)
        self.log_file = str(self.log_file / f'{time_of_date}_logs.txt')
        self.percepts_file = str(self.percepts_file / f'{time_of_date}_percepts.txt')

    def register_perceptions(self, percepts, roles, agent_percepts, seed):
        events = agent_percepts[1].copy()

        for event in events:
            if event == 'flood' and events[event]:
                events[event] = events[event].json()
            else:
                aux = []
                for x in events[event]:
                    if not isinstance(x, str):
                        aux.append(x.json())
                events[event] = aux

        with open(self.percepts_file, 'w') as file:
            file.write(f'Agent perceptions: \n{json.dumps(agent_percepts[0], indent=4)}\n'
                       f'{json.dumps(events, indent=4)}'
                       f'\nMap perceptions: \n{json.dumps(percepts, indent=4)}'
                       f'\nRoles: {"; ".join(roles)}'
                       f'\nSeed: {seed}')

    def register_agent_connection(self, token, name, role):
        hour = datetime.today().hour
        minute = datetime.today().minute
        second = datetime.today().second

        with open(self.log_file, 'a+') as file:
            file.write(f'\nAgent of token: {token}, role: {role} and name: {name}; connected to the '
                       f'simulation at {hour}:{minute}:{second} in {round(time.time() - self.timer, 3)} seconds\n')
            file.write(f'\n{"="*100}\n')

    def register_agent_action(self, token=None, name=None, role=None, action=None, parameters=None,
                              result='No action done'):
        hour = datetime.today().hour
        minute = datetime.today().minute
        second = datetime.today().second

        with open(self.log_file, 'a+') as file:
            file.write(f'\nAgent of token: {token}, role: {role} and name: {name} tried to {action} '
                       f'passing {parameters} at {hour}:{minute}:{second}. The result was {result}\n')
            file.write(f'\n{"="*100}\n')

    def register_end_of_simulation(self, total_of_floods, total_of_victims, total_of_photos, total_of_water_samples,
                                   steps, completed_tasks):
        hour = datetime.today().hour
        minute = datetime.today().minute
        second = datetime.today().second

        with open(self.log_file, 'w') as file:
            file.write(f'\nThe simulation ended with {steps} steps in {round(time.time() - self.timer, 3)} '
                       f'at {hour}:{minute}:{second}. It had {total_of_floods} floods,'
                       f' {total_of_victims} victims, {total_of_photos} photos,'
                       f' {total_of_water_samples} water_samples\n')
            victims, photos, water_samples = completed_tasks
            file.write(f'The amount of completed events victims: {len(victims)}, '
                       f'photos: {len(photos)} and water samples: {len(water_samples)}\n')

            file.write(f'\n{"="*100}\n')
