class Logger:
    __instance = None
    TAG_NORMAL = 'NORMAL'
    TAG_ERROR = 'ERROR'
    TAG_CRITICAL = 'CRITICAL'
    TAG_CONNECT = 'CONNECT'
    TAG_DISCONNECT = 'DISCONNECT'
    TAG_MESSAGE = 'MESSAGE'
    TAG_LOG = 'LOG'
    TAG_API = 'API'

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception('THis class is a singleton!')
        else:
            Logger.__instance = self

    @staticmethod
    def instance():
        if Logger.__instance is None:
            Logger()

        return Logger.__instance

    @staticmethod
    def normal(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_NORMAL} ] ## {message}')

    @staticmethod
    def error(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_ERROR} ] ## {message}')

    @staticmethod
    def critical(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_CRITICAL} ] ## {message}')

    @staticmethod
    def connect(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_CONNECT} ] ## {message}')

    @staticmethod
    def disconnect(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_DISCONNECT} ] ## {message}')

    @staticmethod
    def message(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_MESSAGE} ] ## {message}')

    @staticmethod
    def log(message):
        print(f'[ {Logger.TAG_API} ][ {Logger.TAG_LOG} ] ## {message}')
