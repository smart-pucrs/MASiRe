from monitor_engine.helpers.match import Match


class MonitorManager:

    def __init__(self):
        self.sim_config = None
        self.sim_report = None
        self.matches = []

    def create_new_match(self):
        match = dict(map=None, steps=[], report=None)
        self.matches.append(match)

    def add_match_step(self, match, step_info):
        self.matches[match].steps.append(step_info)

    def add_match(self, map_info):
        self.matches.append(Match(map_info))

    def set_match_report(self, match, report_info):
        self.matches[match].report = report_info

    def get_match_map(self, match):
        return self.matches[match].map_config

    def get_match_step(self, match, step):
        return self.matches[match].steps[step]

    def get_match_report(self, match):
        return self.matches[match].report

    def get_total_matches(self):
        return len(self.matches)

    def get_sim_report(self):
        return self.sim_report

    def get_sim_config(self):
        return self.sim_config

    def check_match_id(self, match):
        return 0 <= match < len(self.matches)

    def check_step_id(self, match, step):
        return 0 <= step < len(self.matches[match].steps)

    def check_sim_config(self):
        return self.sim_config is not None

    def check_sim_report(self):
        return self.sim_report is not None

    def set_sim_config(self, sim_config):
        self.sim_config = sim_config

    def set_sim_report(self, sim_report):
        self.sim_report = sim_report

    def load_simulation(self, replay_data):
        self.sim_config = replay_data['simulation_config']
        self.sim_report = replay_data['simulation_report']
        self.matches = [Match(match['map_percepts'], match['steps'], match['report']) for match in replay_data['matches']]

    def format_simulation_data(self):
        data = dict(
            simulation_config=self.sim_config,
            matches=[dict(map_percepts=match.map_config,
                          steps=match.steps,
                          report=match.report) for match in self.matches],
            simulation_report=self.sim_report
        )

        return data
