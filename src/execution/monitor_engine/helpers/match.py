class Match:

    def __init__(self, map_config, steps=None, report=None):
        if steps:
            self.steps = steps
        else:
            self.steps = []

        self.map_config = map_config
        self.current_step = 0
        self.report = report

    def add_step(self, step):
        self.steps.append(step)

