class Match:

    def __init__(self, map_config, steps=None, report=None):
        if steps:
            self.steps = steps
        else:
            self.steps = []

        self.map_config = map_config
        self.report = report

    def add_step(self, step):
        self.steps.append(step)

    def get_total_steps(self):
        return len(self.steps)

    def get_step(self, step):
        return self.steps[step]

    def __repr__(self):
        return str(self.__dict__)
