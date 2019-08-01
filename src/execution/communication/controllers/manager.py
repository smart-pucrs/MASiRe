from communication.helpers.agents_manager import AgentsManager
from communication.helpers.social_assets_manager import SocialAssetsManager
from communication.helpers.sockets_manager import SocketsManager


class Manager:
    """Class that will handle all the changes on agents, social assets and sockets. Every change must be done here."""

    def __init__(self):
        self.agents_manager = AgentsManager()
        self.social_assets_manager = SocialAssetsManager()
        self.agents_sockets_manager = SocketsManager()
        self.assets_sockets_manager = SocketsManager()

    def add(self, token, obj_info, kind):
        """Add an actor to the corresponding manager.

        :param token: The generated token for the actor.
        :param obj_info: The actor info sent ot the API or gotten on the request,
        :param kind: Either agent, social asset or socket.

        :return bool: True if the token was added else False."""

        if kind == 'agent':
            self.agents_manager.add_agent(token, obj_info)

        elif kind == 'social_asset':
            self.social_assets_manager.add_social_asset(token, obj_info)

        elif kind == 'socket':
            if self.agents_manager.get_agent(token) is None:
                self.assets_sockets_manager.add_socket(token, obj_info)

            else:
                self.agents_sockets_manager.add_socket(token, obj_info)

        else:
            return False

        return True

    def get(self, token, kind):
        """Get the actor or socket requested.

        :param token: The token of the actor requested.
        :param kind: Either agent, social asset or socket.
        :return Agent|SocialAsset|int|None: If neither the actor or socket is found return None."""

        if kind == 'agent':
            return self.agents_manager.get_agent(token)

        elif kind == 'social_asset':
            return self.social_assets_manager.get_social_asset(token)

        elif kind == 'socket':
            if self.agents_manager.get_agent(token) is None:
                return self.assets_sockets_manager.get_socket(token)

            else:
                return self.agents_sockets_manager.get_socket(token)

        else:
            return None

    def get_all(self, kind):
        """Get all the agents, social assets or sockets registered.
        
        :param kind: Either agent, social asset or socket.
        :return list|None: All the agents, social assets, sockets or None."""

        if kind == 'agent':
            return self.agents_manager.get_agents()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_social_assets()

        elif kind == 'socket':
            return self.agents_sockets_manager.get_sockets(), self.assets_sockets_manager.get_sockets()

        else:
            return None

    def get_actions(self, kind):
        """Get all the actions from agents or social assets.

        :param kind: Either agent or social asset.
        :return list|None: All the agents actions, social assets actions or None."""

        if kind == 'agent':
            return self.agents_manager.get_actions()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_actions()

        else:
            return None

    def get_workers(self, kind):
        """Get all the worker agents or social assets.

        :param kind: Either agent or social asset.
        :return list|None: All the worker agents, worker social assets or None."""

        if kind == 'agent':
            return self.agents_manager.get_workers()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_workers()

        else:
            return None

    def get_kind(self, token):
        """Return the kind of the token.

        Note: Equal tokens will cause errors, send different information to the API to get different tokens.

        :param token: The token that is intended to know its kind (agent or social asset).
        :return str|None: Return either agent, social asset or None if it was not found."""

        if self.get(token, 'agent') is None:
            if self.get(token, 'social_asset') is None:
                return None
            return 'social_asset'
        return 'agent'

    def edit(self, token, attribute, new_value, kind):
        """Edit the object identified by the token.

        :param token: The object identifier.
        :param attribute: The attribute of the object that will be changed.
        :param new_value: The new value for the attribute changed.
        :param kind: Either agent or social asset.
        :return bool: True if edited, else false."""

        if kind == 'agent':
            self.agents_manager.edit_agent(token, attribute, new_value)

        elif kind == 'social_asset':
            self.social_assets_manager.edit_social_asset(token, attribute, new_value)

        else:
            return False

        return True

    def clear_workers(self):
        """Clear all the worker agents and worker social assets.

        :return bool: True if cleared else False."""

        try:
            self.agents_manager.clear_workers()
            self.social_assets_manager.clear_workers()
            return True

        except Exception:
            return False

    def remove(self, token, kind):
        """Remove a agent or social asset.

        Note: When removing either one, it will also remove its socket.

        :param token: The identifier for the agent or social asset.
        :param kind: Either agent or social asset.
        :return bool: True if removed else False."""

        if kind == 'agent':
            self.agents_manager.remove_agent(token)
            self.agents_sockets_manager.remove_socket(token)

        elif kind == 'social_asset':
            self.social_assets_manager.remove_social_asset(token)
            self.assets_sockets_manager.remove_socket(token)

        else:
            return False

        return True
