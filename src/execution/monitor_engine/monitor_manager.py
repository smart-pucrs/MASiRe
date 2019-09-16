class MonitorManager:

    def __init__():
        self.current_match = 0
        self.monitor_match = 0
        self.current_step = 0
        self.simulation_info = {}
        self.matchs = []

    def init_replay_mode(replay):
        replay_path = os.getcwd() + '/replays/' + replay
        
        try:
            replay_data = json.loads(open(replay_path, 'r').read())

            self.simulation_info = replay_data['simulation_data']
            self.matchs = replay_data['matchs']

            return True, 'Ok.'

        except Exception as e:
            return False, str(e)


    def init_live_mode(config):
        try:
            config_location = os.getcwd() + '/' + config
            maps = json.load(open(config_location, 'r'))['map']['maps']

            for map_info in maps:
                self.matchs.append({'map': map_info, 'steps_data': []})

        except Exception as e:
            print(f'[ MONITOR ][ ERROR ] ## Unknown error: {str(e)}')

    
    def set_simulation_info(simulation_info):
        self.simulation_info = simulation_info

    
    def save_replay():
        current_date = date.today().strftime('%d-%m-%Y')
        hours = time.strftime("%H:%M:%S")
        file_name = f'REPLAY_of_{current_date}_at_{hours}.txt'

        abs_path = os.getcwd() + '/replays/'
        replay_data = {'simulation_info': self.simulation_info,
                       'matchs'> self.matchs}

        try:
            with open(str(abs_path + file_name), 'w+') as file:
                file.write(json.dumps(replay_data, sort_keys=False, indent=4))

            return True, 'Ok.'
        
        except Exception as e:
            return False, str(e)


    def get_initial_information():
        map_info = self.matchs[self.monitor_match]['map']

        total_matchs = len(self.matchs)
        match_info = {'current_match': self.current_match, 'total_matchs': total_matchs}

        return {
            'simulation_info': self.simulation_info,
            'map_info': self.matchs[self.monitor_match]['map'],
            'match_info': match_info
        }

    def next_match_api():
        self.current_match += 1

    def add_step_data(step_data):
        self.matchs[self.current_match].append(step_data)


    def next_step():
        if self.current_step == 0:
            raise Exception('Last step.')
    
        self.current_step += 1
        
        return self.get_step_data()
    
    
    def prev_step():
        if self.current_step == 0:
            raise Exception('First step.')
    
        self.current_step -= 1
        
        return self.get_step_data()


    def get_step_data():
        step = self.current_step
        step_data = self.matchs[self.monitor_match]['steps_data'][step]
        total_steps = len(self.matchs[self.monitor_match]['steps_data'][step])
        
        return {'current_step': step,
                'total_steps': total_steps,
                'step_data': step_data}



    def prev_match():
        if self.monitor_match == 0:
            raise Exception('First match.')

        self.monitor_match -= 1
        self.current_step = 0

        return self.get_match_data()

    def next_match():
        if self.monitor_match > len(self.matchs)-1:
            raise Exception('Last match.')

        self.monitor_match += 1
        self.current_step = 0

        return self.get_match_data()

    def get_match_data():
        step = self.current_step
        total_matchs = len(self.matchs)
        current_match = self.monitor_match
        map_info = self.match[current_match]['map']
        total_steps = len(self.matchs[current_match]['steps_data'])
        step_data = self.matchs[current_match]['steps_data'][step]

        return {
            'step': step,
            'total_steps': total_steps,
            'current_match': current_match,
            'total_matchs': total_matchs,
            'step_data': step_data,
            'map_info': map_info
        }