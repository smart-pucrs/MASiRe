import random
from collections import namedtuple
from simulation_engine.simulation_objects.social_asset import SocialAsset


Capacities = namedtuple('Capacities', 'abilities resources location profession size speed physical_capacity virtual_capacity')


class SocialAssetsManager:
    """Class that will handle all the changes on the social assets inside the engine."""

    def __init__(self, map_info, social_assets_info, social_assets_markers):
        self.social_assets = {}
        self.social_assets_markers = social_assets_markers
        self.cdm_location = [map_info['maps'][0]['centerLat'], map_info['maps'][0]['centerLon']]
        random.seed(map_info['randomSeed'])
        self.requests = {}
        self.social_assets_info = social_assets_info

    def restart(self, map_info, social_assets_info, social_assets_markers):
        self.social_assets.clear()
        self.social_assets_markers = social_assets_markers
        self.cdm_location = [map_info['maps'][0]['centerLat'], map_info['maps'][0]['centerLon']]
        random.seed(map_info['randomSeed'])
        self.requests.clear()
        self.social_assets_info = social_assets_info

    def connect(self, token, id, profession):
        abilities = self.social_assets_info[profession]['abilities']
        resources = self.social_assets_info[profession]['resources']
        location = self.cdm_location
        size = random.randint(self.social_assets_info[profession]['minSize'],
                              self.social_assets_info[profession]['maxSize'])
        speed = self.social_assets_info[profession]['speed']
        physical_capacity = self.social_assets_info[profession]['physicalCapacity']
        virtual_capacity = self.social_assets_info[profession]['virtualCapacity']

        social_asset = SocialAsset(id, token, abilities, resources, location,
                                   profession, size, speed, physical_capacity, virtual_capacity)

        self.social_assets[token] = social_asset

        return self.social_assets[token]

    def finish_connections(self):
        for identifier in self.requests.values():
            self.set_marker_status(identifier, True)

        self.requests.clear()

    def set_marker_status(self, identifier, status):
        """Set the active attribute of the marker given.

        :param identifier: id of asset marker.
        :param status: true to enable marker, false to disable.
        """

        for marker in self.social_assets_markers:
            if marker.identifier == identifier:
                marker.active = status
                break

    def disconnect(self, token):
        """Disconnect the social asset if it was connected.

        :param token: The identifier of the social asset.
        :return bool: True if the agent was disconnected, else False."""

        if token not in self.social_assets:
            return False

        else:
            self.social_assets[token].disconnect()
            return True

    def add_physical(self, token, item):
        """Add a physical item to the requested social asset.

        :param token: Identifier of the requested social asset.
        :param item: Item to be added."""

        self.social_assets[token].add_physical_item(item)

    def add_virtual(self, token, item):
        """Add a virtual item to the requested social asset.

        :param token: Identifier of the requested social asset.
        :param item: Item to be added."""

        self.social_assets[token].add_virtual_item(item)

    def add(self, token, social_asset):
        """Add a social asset to the requested social asset.

        :param token: Identifier of the requested social asset.
        :param social_asset: Social asset searched by the social asset."""

        self.social_assets[token].social_assets.append(social_asset)

    def get(self, token):
        """Get the SocialAsset object saved inside the engine.

        :param token: The identifier of the requested social asset.
        :return Agent|None: Return the SocialAsset object or None if not found."""

        return self.social_assets.get(token)

    def get_tokens(self):
        """Get all the connected tokens.

        :return list: List of all the active social assets tokens."""

        return [token for token in self.social_assets if self.social_assets[token].is_active]

    def get_info(self):
        """Get all the information saved from the social assets.

        :return list: List of all the social assets objects."""

        return list(self.social_assets.values())

    def get_active_info(self):
        """Get all the information saved from the social assets that are active.

        :return list: List of all the active social assets objects."""

        return [self.social_assets[token] for token in self.social_assets if self.social_assets[token].is_active]

    def deliver_physical(self, token, kind, amount=1):
        """Deliver a physical item from the requested social asset.

        :param token: The identifier of the requested social asset.
        :param kind: The type of the item to be removed.
        :param amount: The amount of items to be removed.
        :return list: List of removed items."""

        return self.social_assets[token].remove_physical_item(kind, amount)

    def deliver_agent(self, token, target_token):
        """Deliver a agent item from the requested agent.

        :param token: The identifier of the requested agent.
        :param target_token: The identifier of the agent to be removed.
        :return agent: The agent removed."""

        return self.social_assets[token].remove_agent_item(target_token)

    def deliver_virtual(self, token, kind, amount=1):
        """Deliver a virtual item from the requested social asset.

        :param token: The identifier of the requested social asset.
        :param kind: The type of the item to be removed.
        :param amount: The amount of items to be removed.
        :return list: List of removed items."""

        return self.social_assets[token].remove_virtual_item(kind, amount)

    def edit(self, token, attribute, new_value):
        """Edit the requested social asset.

        :param token: The identifier of the requested social asset.
        :param attribute: The attribute to be edited from the social asset.
        :param new_value: The new value for the attribute."""

        exec(f'self.social_assets[token].{attribute} = new_value')

    def update_location(self, token):
        """Update the social asset location based on the remaining locations on its route.

        :param token: The identifier of the requested social asset."""

        if self.social_assets[token].route:
            location = self.social_assets[token].route.pop(0)[:-1]
            self.social_assets[token].location = location

    def clear_physical_storage(self, token):
        """Clear the physical storage of the requested social asset.

        :param token: The identifier of the requested social asset."""

        self.social_assets[token].clear_physical_storage()

    def clear_virtual_storage(self, token):
        """Clear the virtual storage of the requested social asset.

        :param token: The identifier of the requested social asset."""

        self.social_assets[token].clear_virtual_storage()

    def get_assets_markers(self):
        return self.social_assets_markers
