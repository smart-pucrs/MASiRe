class Logger:
    __instance = None
    TAG_NORMAL = 'NORMAL'
    TAG_ERROR = 'ERROR'
    TAG_CRITICAL = 'CRITICAL'
    TAG_SIMULATOR = 'SIMULATOR'

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
    def log(tag, message):
        print(f'[ API ][ {tag} ] ## {message}')

    @staticmethod
    def normal(message):
        print(f'[ {Logger.TAG_SIMULATOR} ][ {Logger.TAG_NORMAL} ] ## {message}')

    @staticmethod
    def error(message):
        print(f'[ {Logger.TAG_SIMULATOR} ][ {Logger.TAG_ERROR} ] ## {message}')

    @staticmethod
    def critical(message):
        print(f'[ {Logger.TAG_SIMULATOR} ][ {Logger.TAG_CRITICAL} ] ## {message}')