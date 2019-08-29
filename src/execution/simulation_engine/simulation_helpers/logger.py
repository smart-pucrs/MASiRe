class Logger:
    __instance = None

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
        print(f'[ SIMULATION ][ {tag} ] ## {message}')