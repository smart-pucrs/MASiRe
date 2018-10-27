import time

class Controller:

    def __init__(self):
        self.agents=[]
        self.timer = time.time()
        self.init_general = None

    def check_population(self):
        if self.init_general is None:
            self.init_general = time.time()

        if self.check_timeraux():
            if len(self.agents) > 5:
                return True
            else:
                return False

    def check_timer(self):
        if time.time() - self.init_general < 3600:
            return True
        else:
            return False
