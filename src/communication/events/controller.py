import time

class Controller:

    def __init__(self):
        self.agents=[]
        self.timer = time.time()
        self.init_general = None

    #initializes the timer if it has not been initialized
    #check if the total agents exceeded
    def check_population(self):
        if self.init_general is None:
            self.init_general = time.time()

        if self.check_timer():
            if len(self.agents) > 5:
                return True
            else:
                return False
    #check if connection period for new agents is open
    def check_timer(self):
        if time.time() - self.init_general < 3600:
            return True
        else:
            return False
