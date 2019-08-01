class FailedWrongParam(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return 'FailedWrongParam: ' + self.message


class FailedUnknownFacility(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return 'FailedUnknownFacility: ' + self.message


class FailedNoRoute(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return 'FailedNoRoute: ' + self.message


class FailedCapacity(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedCapacity: ' + self.message


class FailedLocation(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedLocation: ' + self.message


class FailedUnknownItem(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedUnknownItem: ' + self.message


class FailedItemAmount(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedItemAmount: ' + self.message


class FailedInvalidKind(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedInvalidKind: ' + self.message


class FailedInsufficientBattery(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedInsufficientBattery: ' + self.message


class FailedNoSocialAsset(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedNoSocialAsset: ' + self.message


class UnableToReach(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'UnableToReach: ' + self.message


class FailedUnknownToken(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedUnknownToken: ' + self.message


class FailedNoMatch(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'FailedNoMatch: ' + self.message
