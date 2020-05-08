class Report(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Report, cls).__new__(cls)
            cls.total_events = 0
            cls._victim = _Victim()
            cls.victims = property(fget=lambda self: self._victim)
            cls._photo = _Photo()
            cls.photos = property(fget=lambda self: self._photo)
            cls._sample = _Sample()
            cls.samples = property(fget=lambda self: self._sample)
        return cls.instance

class _Victim(object):
    def __init__(self):
        self._known = 0
        self._hidden = 0
        self._rescued_alive = 0
        self._rescued_dead = 0

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



