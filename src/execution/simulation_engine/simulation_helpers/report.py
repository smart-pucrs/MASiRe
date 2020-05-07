class Report(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Report, cls).__new__(cls)
            cls.total_events = 0
            cls.total_victims = 0
            cls.total_photos = 0
            cls.total_samples = 0
        return cls.instance
    
    # def __init__(self):
    #     self.total_events = 0
    #     self.total_victims = 0
    #     self.total_photos = 0
    #     self.total_samples = 0


