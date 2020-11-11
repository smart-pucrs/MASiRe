import time
from communication.objects.social_asset import SocialAsset


class SocialAssetsManager:
    """Class that will handle all the changes on social assets. Every change on social assets must be done here."""

    def __init__(self):
        self.social_assets = {}

    def add_social_asset(self, token, asset_info):
        """Add a social asset to the dictionary.

        The key is the generated token and the value if the SocialAsset object.

        :param token: The generated token for the social asset.
        :param asset_info: The information sent to the API by the social asset."""

        self.social_assets[token] = SocialAsset(token, asset_info)

    def get_social_asset(self, token):
        """Get the social asset object if the token is registered.

        :param token: The generated token for the social asset requested.
        :return SocialAsset|None: The registered agent or None if it was not registered."""

        return self.social_assets.get(token)

    def get_social_assets(self):
        """Get all the registered social assets.

        :return list: All the social assets objects."""

        return list(self.social_assets.values())

    def get_actions(self):
        """Return a list of all the actions that the social assets have sent to the simulation on the previous step.

        Note: RuntimeError can occur if the gap between validating the action and ending the step occur, to prevent that,
        it will wait one second after the error and then proceed. If the error happens again, then it must be some
        internal error that are allowing the social assets to send actions after the step is finished.

        :return list: All the actions sent on the previous step."""

        actions = []
        try:
            for token in self.social_assets:
                if self.social_assets[token].worker:
                    action_name = self.social_assets[token].action_name
                    action_params = self.social_assets[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        except RuntimeError:
            time.sleep(1)
            actions = []
            for token in self.social_assets:
                if self.social_assets[token].worker:
                    action_name = self.social_assets[token].action_name
                    action_params = self.social_assets[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        return actions

    def get_workers(self):
        """Get all the workers. The social asset is considered a worker if it sent an action on the previous step.

        :return list: All the social assets objects."""

        return [self.social_assets[token] for token in self.social_assets if self.social_assets[token].worker]

    def edit_social_asset(self, token, attribute, new_value):
        """Edit an attribute of some social asset.

        :param token: The token of some social asset that will be edited.
        :param attribute: The attribute of the social asset that will be edited.
        :param new_value: The new value for the attribute given."""

        exec(f'self.social_assets[token].{attribute} = new_value')

    def clear_workers(self):
        """Clear all the workers. After the end of the step, all the workers are cleared so they have to send actions
        on the next step."""

        for token in self.social_assets:
            self.social_assets[token].worker = False

    def remove_social_asset(self, token):
        """Remove a social asset from the dictionary.

        :param token: The generated token that will be removed from the dictionary."""

        del self.social_assets[token]
