
class SocialAsset:
    """Class that represents the connected social asset. It does not hold all the information that the social asset has,
    but only the necessary to connect and send actions to the engine."""

    def __init__(self, token, obj):
        self.token = token
        self.registered = False
        self.worker = False
        self.action_name = ''
        self.action_params = []
        self.asset_info = obj

