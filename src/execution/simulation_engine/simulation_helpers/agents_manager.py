from collections import namedtuple
from simulation_engine.simulation_objects.agent import Agent

Role = namedtuple('Role', 'abilities resources size name battery speed physical_capacity virtual_capacity')


class AgentsManager:
    """Class that will handle all the changes on the agents inside the engine."""

    def __init__(self, roles_info, cdm_location):
        self.agents = {}
        self.cdm_location = cdm_location
        self.roles = self.generate_roles(roles_info)

    def restart(self, roles_info, cdm_location):
        """Restart the class by erasing all the agents and recreating them with the same tokens.

        :param roles_info: The information of the roles available (car, drone, boat).
        :param cdm_location: The location of the cdm."""

        tokens = list(self.agents.keys())
        self.agents.clear()
        self.cdm_location = cdm_location
        self.roles.clear()
        self.roles = self.generate_roles(roles_info)
        for token in tokens:
            self.connect(token)

    @staticmethod
    def generate_roles(roles_info):
        """Generate roles for the agents.

        :param roles_info: The information of the available roles (car, drone, boat).
        :return list: List with all the generated roles ready to be given to the agents."""

        roles = []
        for role in roles_info:
            temp_role = Role(
                roles_info[role]['abilities'],
                roles_info[role]['resources'],
                roles_info[role]['size'],
                role,
                roles_info[role]['battery'],
                roles_info[role]['speed'],
                roles_info[role]['physicalCapacity'],
                roles_info[role]['virtualCapacity'])
            for i in range(roles_info[role]['amount']):
                roles.append(temp_role)

        return roles

    def connect(self, token):
        """Connect the agent if there are roles still available.

        :param token: The identifier of the agent.
        :return bool: True if the agent was added else False."""

        if not self.roles:
            return False

        role = self.roles.pop(0)
        self.agents[token] = Agent(token, self.cdm_location, *role)

        return True

    def disconnect(self, token):
        """Disconnect the agent if it was connected.

        :param token: The identifier of the agent.
        :return bool: True if the agent was disconnected, else False."""

        if token not in self.agents:
            return False

        else:
            self.agents[token].disconnect()
            return True

    def add_physical(self, token, item):
        """Add a physical item to the requested agent.

        :param token: Identifier of the requested agent.
        :param item: Item to be added."""

        self.agents[token].add_physical_item(item)

    def add_virtual(self, token, item):
        """Add a virtual item to the requested agent.

        :param token: Identifier of the requested agent.
        :param item: Item to be added."""

        self.agents[token].add_virtual_item(item)

    def add(self, token, social_asset):
        """Add a social asset to the requested agent.

        :param token: Identifier of the requested agent.
        :param social_asset: Social asset searched by the agent."""

        self.agents[token].social_assets.append(social_asset)

    def charge(self, token):
        """Charge the requested agent.

        :param token: The identifier of the requested agent."""

        self.agents[token].charge()

    def discharge(self, token):
        """Discharge the requestede agent.

        :param token: The identifier of the requested agent."""

        self.agents[token].discharge()

    def get(self, token):
        """Get the Agent object saved inside the engine.

        :param token: The identifier of the requested agent.
        :return Agent|None: Return the Agent object or None if not found."""

        return self.agents.get(token)

    def get_tokens(self):
        """Get all the connected tokens.

        :return list: List of all the active agents tokens."""

        return [token for token in self.agents if self.agents[token].is_active]

    def get_info(self):
        """Get all the information saved from the agents.

        :return list: List of all the agents objects."""

        return list(self.agents.values())

    def get_active_info(self):
        """Get all the information saved from the agents that are active.

        :return list: List of all the active agents objects."""

        return [self.agents[token] for token in self.agents if self.agents[token].is_active]

    def deliver_physical(self, token, kind, amount=1):
        """Deliver a physical item from the requested agent.

        :param token: The identifier of the requested agent.
        :param kind: The type of the item to be removed.
        :param amount: The amount of items to be removed.
        :return list: List of removed items."""

        return self.agents[token].remove_physical_item(kind, amount)

    def deliver_virtual(self, token, kind, amount=1):
        """Deliver a virtual item from the requested agent.

        :param token: The identifier of the requested agent.
        :param kind: The type of the item to be removed.
        :param amount: The amount of items to be removed.
        :return list: List of removed items."""

        return self.agents[token].remove_virtual_item(kind, amount)

    def edit(self, token, attribute, new_value):
        """Edit the requested agent.

        :param token: The identifier of the requested agent.
        :param attribute: The attribute to be edited from the agent.
        :param new_value: The new value for the attribute."""

        exec(f'self.agents[token].{attribute} = new_value')

    def update_location(self, token):
        """Update the agent location based on the remaining locations on its route.

        :param token: The identifier of the requested agent."""

        if self.agents[token].route:
            location = self.agents[token].route.pop(0)
            self.agents[token].location = location

    def clear_physical_storage(self, token):
        """Clear the physical storage of the requested agent.

        :param token: The identifier of the requested agent."""

        self.agents[token].clear_physical_storage()

    def clear_virtual_storage(self, token):
        """Clear the virtual storage of the requested agent.

        :param token: The identifier of the requested agent."""

        self.agents[token].clear_virtual_storage()
