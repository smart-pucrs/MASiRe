"""
[All the exceptions constructors, which are initiated by a desired error message.]
"""

class Failed_wrong_param(Exception):

    def __init__(self, message=None):
        self.message = message


class Failed_unknown_facility(Exception):

    def __init__(self, message=None):
        self.message = message


class Failed_no_route(Exception):

    def __init__(self, message=None):
        self.message = message


class Failed_capacity(Exception):

    def __init__(self, message):
        self.message = message


class Failed_location(Exception):

    def __init__(self, message):
        self.message = message


class Failed_unknown_item(Exception):

    def __init__(self, message):
        self.message = message


class Failed_item_amount(Exception):

    def __init__(self, message):
        self.message = message


class Failed_invalid_kind(Exception):

    def __init__(self, message):
        self.message = message


class Failed_insufficient_battery(Exception):

    def __init__(self, message):
        self.message = message
