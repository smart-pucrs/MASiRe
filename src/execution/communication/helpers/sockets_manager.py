

class SocketsManager:
    """Class that will handle all the changes on sockets. Every change on sockets must be done here."""

    def __init__(self):
        self.socket_clients = {}

    def add_socket(self, token, socket_id):
        """Add a socket to the dictionary.

        The key is the generated token and the value if the socket id.

        :param token: The generated token for the actor.
        :param socket_id: The socket id captured during the connection."""

        self.socket_clients[token] = socket_id

    def get_socket(self, token):
        """Get the socket id if the token is registered.

        :param token: The generated token for the actor.
        :return SocketID|None: The registered id or None if it was not registered."""

        return self.socket_clients.get(token)

    def get_sockets(self):
        """Get all the registered sockets ids.

        :return list: All the sockets ids."""

        return list(self.socket_clients.values())

    def get_tokens(self):
        """Get all the registered tokens.

        :return list: All the tokens."""

        return list(self.socket_clients.keys())

    def remove_socket(self, token):
        """Remove a socket from the dictionary.

        :param token: The generated token that will be removed from the dictionary."""

        del self.socket_clients[token]
