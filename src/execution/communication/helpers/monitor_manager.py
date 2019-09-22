class MonitorManager:

    def __init__(self):
        self.monitors = []
    
    def add_monitor(self, sid):
        if sid in self.monitors:
            return False

        self.monitors.append(sid)
        
        return True

    def rmv_monitor(self, sid):
        if sid not in self.monitors:
            return False

        self.monitors.remove(sid)

        return True

    def get_rooms(self):
        return self.monitors