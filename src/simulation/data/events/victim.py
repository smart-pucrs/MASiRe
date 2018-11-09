class Victim:

    def __init__(self, id, size, lifetime, node):
        self.id = id
        self.size = size
        self.lifetime = lifetime
        self.active = False
        self.node = node