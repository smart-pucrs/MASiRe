class MASiReException(Exception):
    def __init__(self, id:str, message=None):
        self.message = message
        self.identifier = id

    def __str__(self):
        return f'{self.__class__.__name__}: ' + self.message

class FailedWrongParam(MASiReException):
    def __init__(self, message=None):
        super(FailedWrongParam, self).__init__(id='wrongParam', message=message)

class FailedUnknownFacility(MASiReException):
    def __init__(self, message=None):
        super(FailedUnknownFacility, self).__init__(id='unknownFacility', message=message)

class FailedNoRoute(MASiReException):
    def __init__(self, message=None):
        super(FailedNoRoute, self).__init__(id='noRoute', message=message)

class FailedCapacity(MASiReException):
    def __init__(self, message=None):
        super(FailedCapacity, self).__init__(id='noCapacity', message=message)

class FailedLocation(MASiReException):
    def __init__(self, message=None):
        super(FailedLocation, self).__init__(id='noLocation', message=message)

class FailedUnknownItem(MASiReException):
    def __init__(self, message=None):
        super(FailedUnknownItem, self).__init__(id='unknownItem', message=message)

class FailedItemAmount(MASiReException):
    def __init__(self, message=None):
        super(FailedItemAmount, self).__init__(id='itemAmount', message=message)

class FailedInvalidKind(MASiReException):
    def __init__(self, message=None):
        super(FailedInvalidKind, self).__init__(id='invalidType', message=message)

class FailedInsufficientBattery(MASiReException):
    def __init__(self, message=None):
        super(FailedInsufficientBattery, self).__init__(id='noBattery', message=message)

class FailedNoSocialAsset(MASiReException):
    def __init__(self, message=None):
        super(FailedNoSocialAsset, self).__init__(id='noSocialAsset', message=message)

class FailedUnknownToken(MASiReException):
    def __init__(self, message=None):
        super(FailedUnknownToken, self).__init__(id='unknownToken', message=message)

class FailedSocialAssetRequest(MASiReException):
    def __init__(self, message=None):
        super(FailedSocialAssetRequest, self).__init__(id='socialAssetRequest', message=message)

class FailedNoMatch(MASiReException):
    def __init__(self, message=None):
        super(FailedNoMatch, self).__init__(id='noMatch', message=message)

class FailedParameterType(MASiReException):
    def __init__(self, message=None):
        super(FailedParameterType, self).__init__(id='parameterType', message=message)

class NoActionsAllowed(MASiReException):
    def __init__(self, message=None):
        super(NoActionsAllowed, self).__init__(id='cannotPerformActions', message=message)

class NotActive(MASiReException):
    def __init__(self, message=None):
        super(NotActive, self).__init__(id='agentNotActive', message=message)
