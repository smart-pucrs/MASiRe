class AssetRequestManager:
    """ Class responsible to managing the social assets requests."""
    def __init__(self):
        self.main_tokens = {}
        self.assets_tokens = {}
        self.current_step = 0
        self.response = None
        self.processing_requests = False

    def start_new_asset_request(self, response):
        """
        Start a new request.

        :param response: Dict with the response of the current step.
        """

        for token in response['requests']:
            self.main_tokens[token] = None
        self.current_step = response['current_step']
        self.response = response['messages']
        self.processing_requests = True

    def reset(self):
        """
        Reset all values of the old request.

        """
        self.main_tokens = {}
        self.assets_tokens = {}
        self.current_step = 0
        self.response = {}
        self.processing_requests = False

    def check_token_request(self, token):
        """
        Checks if the entered token is in the list of tokens that called a social asset.

        :param token: Str the token to verify.
        :return Bool: True if the token is in the list else False.
        """
        return token in self.main_tokens

    def check_step(self, step):
        """
        Checks if the current step is the same of the step informed by the agent.

        :param step: Int current step.
        :return Bool: True if the step checks else False.
        """
        return self.current_step == step

    def check_asset_token(self, main_token, token):
        """
        Checks if the token informed is the same of the main token have as asset.

        :param main_token: Str token of the agent caller.
        :param token: Str token of the asset.
        :return Bool: True if the main token have the entered token else False.
        """
        return self.main_tokens[main_token] == token

    def add_asset_token(self, main_token, token):
        """
        Add a token into a main token.

        :param main_token: Str token of the agent caller.
        :param token: Str asset token.
        :return Str: The token that was added.
        """
        self.main_tokens[main_token] = token
        return self.main_tokens[main_token]

    def check_requests(self):
        """
        Checks if the all request are handled.

        :return Bool: True if the all request are handled else False.
        """
        for token in self.main_tokens:
            if self.main_tokens[token] is None:
                return False
        return True

    def get_main_token(self, asset_token):
        for token in self.main_tokens:
            if self.main_tokens[token] == asset_token:
                return token

        return None

    def format_actions_result(self, assets_response):
        agents_responses = self.response['actors']
        for agent in agents_responses:
            token = agent['agent']['token']
            if agent['agent']['last_action'] == 'requestSocialAsset' and token in self.main_tokens:
                if self.main_tokens[token] is not None:
                    agent['agent']['last_action_result'] = True
                else:
                    agent['agent']['message'] = 'The Social asset did not connect.'

        agents_responses.extend(assets_response['actors'])
        self.response['actors'] = agents_responses

        return self.response

    def processing(self):
        return self.processing_requests

    def get_social_assets_tokens(self):
        tokens = []

        for main_token in self.main_tokens:
            if self.main_tokens[main_token] is not None:
                tokens.append(self.main_tokens[main_token])

        return tokens
