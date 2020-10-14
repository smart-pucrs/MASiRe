import json 
class Report(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Report, cls).__new__(cls)
            cls.total_events = 0
            cls.instance.victim = _Victim()
            cls.victims = property(fget=lambda self: self.victim)
            cls.instance.photo = _Photo()
            cls.photos = property(fget=lambda self: self.photo)
            cls.instance.sample = _Sample()
            cls.samples = property(fget=lambda self: self.sample)
        return cls.instance
    
    def dict(self):
        return self.__dict__.copy()
    def to_json(self):
        return json.dumps(self.dict(), default=lambda o: o.dict())

class _Victim(object):
    def __init__(self):
        self._known = 0
        self._hidden = 0
        self._rescued_alive = 0
        self._rescued_dead = 0
        self._discovered = 0

    @property
    def total(self):
        return self._known + self._hidden

    @property
    def known(self):
        return self._known
    @known.setter
    def known(self, value):
        self._known += value

    @property
    def hidden(self):
        return self._hidden
    @hidden.setter
    def hidden(self, value):
        self._hidden += value
    
    @property
    def discovered(self):
        return self._hidden
    @discovered.setter
    def discovered(self, value):
        self._discovered += value
    
    @property
    def dead(self):
        return self._rescued_dead
    @dead.setter
    def dead(self, value):
        self._rescued_dead += value

    @property
    def alive(self):
        return self._rescued_alive
    @alive.setter
    def alive(self, value):
        self._rescued_alive += value

    @property
    def ignored(self):
        return self.total - (self._rescued_alive+self._rescued_dead)
    def dict(self):
        return {'known': self.known, 'hidden': self.hidden, 'discovered': self.discovered, 'rescued_alive': self.alive, 'rescued_dead': self.dead}

class _Sample(object):
    def __init__(self):
        self._request = 0
        self._collected = 0

    @property
    def request(self):
        return self._request
    @request.setter
    def request(self, value):
        self._request += value

    @property
    def collected(self):
        return self._collected
    @collected.setter
    def collected(self, value):
        self._collected += value

    @property
    def ignored(self):
        return self._request - self._collected
    def dict(self):
        return {'requested': self.request, 'collected': self.collected}

class _Photo(object):
    def __init__(self):
        self._request = 0
        self._collected = 0
        self._analysed = 0

    @property
    def request(self):
        return self._request
    @request.setter
    def request(self, value):
        self._request += value

    @property
    def analysed(self):
        return self._analysed
    @analysed.setter
    def analysed(self, value):
        self._analysed += value

    @property
    def collected(self):
        return self._collected
    @collected.setter
    def collected(self, value):
        self._collected += value

    @property
    def ignored(self):
        return self._request - self._collected
    def dict(self):
        return {'requested': self.request, 'collected': self.collected, 'analysed': self.analysed}



