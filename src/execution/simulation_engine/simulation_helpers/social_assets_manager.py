import random
from collections import namedtuple
from simulation_engine.simulation_objects.social_asset import SocialAsset


Capacities = namedtuple('Capacities', 'abilities resources location profession size speed physical_capacity virtual_capacity')


class SocialAssetsManager:
    """Class that will handle all the changes on the social assets inside the engine."""

    def __init__(self, map_info, social_assets_info):
        self.social_assets = {}
        random.seed(map_info['randomSeed'])
        self.capacities = self.generate_objects(map_info, social_assets_info)

    def restart(self, map_info, social_assets_info):
        """Restart the class by erasing all the social assets and recreating them with the same tokens.

        :param map_info: Information about the current map.
        :param social_assets_info: The information of the professions available."""

        tokens = list(self.social_assets.keys())
        self.social_assets.clear()
        self.capacities = self.generate_objects(map_info, social_assets_info)
        for token in tokens:
            self.connect(token)

    @staticmethod
    def generate_objects(map_info, social_assets_info):
        """Generate professions for the social assets.

        :param map_info: Information about the current map.
        :param social_assets_info: The information of the professions available.
        :return list: List of all the professions ready to be used by the social assets."""

        min_lon = map_info['minLon']
        max_lon = map_info['maxLon']
        min_lat = map_info['minLat']
        max_lat = map_info['maxLat']

        capacities = []
        for profession in social_assets_info:
            location = random.uniform(min_lon, max_lon), random.uniform(min_lat, max_lat)
            size = random.randint(social_assets_info[profession]['minSize'], social_assets_info[profession]['maxSize'])
            speed = social_assets_info[profession]['speed']
            physical_capacity = social_assets_info[profession]['physicalCapacity']
            virtual_capacity = social_assets_info[profession]['virtualCapacity']
            abilities = social_assets_info[profession]['abilities']
            resources = social_assets_info[profession]['resources']

            temp_capacities = Capacities(abilities, resources, location,
                                         profession, size, speed, physical_capacity, virtual_capacity)

            for i in range(social_assets_info[profession]['amount']):
                capacities.append(temp_capacities)

        return capacities

    def connect(self, token):
        """Connect the social asset if there are professions still available.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was added else False."""

        if not self.capacities:
            return None

        asset_info = self.capacities.pop(0)
        self.social_assets[token] = SocialAsset(token, *asset_info)
        return self.social_assets[token]

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
            location = self.social_assets[token].route.pop(0)
            self.social_assets[token].location = location

    def clear_physical_storage(self, token):
        """Clear the physical storage of the requested social asset.

        :param token: The identifier of the requested social asset."""

        self.social_assets[token].clear_physical_storage()

    def clear_virtual_storage(self, token):
        """Clear the virtual storage of the requested social asset.

        :param token: The identifier of the requested social asset."""

        self.social_assets[token].clear_virtual_storage()
