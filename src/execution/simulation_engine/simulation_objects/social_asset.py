from simulation_engine.exceptions.exceptions import *


class SocialAsset:
    """Class that represents the SocialAsset inside the simulation."""

    def __init__(self, token, abilities, resources, location, profession, size, speed, physical_capacity, virtual_capacity):
        self.token = token
        self.type = 'social_asset'
        self.is_active = True
        self.carried = False
        self.min_size = size
        self.location = location
        self.last_action = None
        self.last_action_result = False
        self.profession = profession
        self.abilities = abilities
        self.resources = resources
        self.speed = speed
        self.route = []
        self.destination_distance = 0
        self.physical_capacity = physical_capacity
        self.physical_storage = physical_capacity
        self.physical_storage_vector = []
        self.virtual_capacity = virtual_capacity
        self.virtual_storage = virtual_capacity
        self.virtual_storage_vector = []
        self.social_assets = []

    @property
    def size(self):
        """Return the size of the social asset based on its current storage weight and its own size.

        :return int: Weight of the social asset."""

        return self.min_size + (self.physical_capacity - self.physical_storage)

    def add_physical_item(self, item):
        """Add a physical item to the storage of the social asset.

        Note: The item must have a size and type attributes.

        :param item: The physical item.
        :raise FailedCapacity: If the size of the item is bigger than the available storage."""

        size = item.size
        if size > self.physical_storage:
            raise FailedCapacity('The asset does not have enough physical storage.')

        self.physical_storage -= size
        self.physical_storage_vector.append(item)

    def add_virtual_item(self, item):
        """Add a virtual item to the storage of the social asset.

        Note: The item must have a size and type attributes.

        :param item: The virtual item.
        :raise FailedCapacity: If the size of the item is bigger than the available storage."""

        size = item.size
        if size > self.virtual_storage:
            raise FailedCapacity('The asset does not have enough physical storage.')

        self.virtual_storage -= size
        self.virtual_storage_vector.append(item)

    def remove_physical_item(self, kind, amount):
        """Remove physical items from the social asset.

        :param kind: The type of the item to be removed
        :param amount: The amount of items of the given type to be removed.
        :raise FailedItemAmount: If the social asset has no physical items.
        :raise FailedUnknownItem: If there is no item with the given kind stored.
        :return list: List of the removed items."""

        if self.physical_storage == self.physical_capacity:
            raise FailedItemAmount('The asset has no physical items to deliver.')

        if not amount:
            return []

        found_item = False
        removed_items = []
        for stored_item in self.physical_storage_vector:
            if kind == stored_item.type and amount:
                found_item = True
                removed_items.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise FailedUnknownItem('No physical item of this type is stored.')

        for removed_item in removed_items:
            self.physical_storage_vector.remove(removed_item)
            self.physical_storage += removed_item.size

        return removed_items

    def remove_virtual_item(self, kind, amount):
        """Remove virtual items from the social asset.

        :param kind: The type of the item to be removed
        :param amount: The amount of items of the given type to be removed.
        :raise FailedItemAmount: If the social asset has no virtual items.
        :raise FailedUnknownItem: If there is no item with the given kind stored.
        :return list: List of the removed items."""

        if self.virtual_storage == self.virtual_capacity:
            raise FailedItemAmount('The social asset has no virtual items to deliver.')

        if not amount:
            return []

        found_item = False
        removed_items = []
        for stored_item in self.virtual_storage_vector:
            if kind == stored_item.type and amount:
                found_item = True
                removed_items.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise FailedUnknownItem('No virtual item of this type is stored.')

        for removed_item in removed_items:
            self.virtual_storage_vector.remove(removed_item)
            self.virtual_storage += removed_item.size

        return removed_items

    def clear_physical_storage(self):
        """Clear the physical storage vector and restore the physical storage to its full capacity."""

        self.physical_storage_vector.clear()
        self.physical_storage = self.physical_capacity

    def clear_virtual_storage(self):
        """Clear the virtual storage vector and restore the virtual storage to its full capacity."""

        self.virtual_storage_vector.clear()
        self.virtual_storage = self.virtual_capacity

    def disconnect(self):
        """Disconnect the social asset.

        It would not be good to just erase the social asset from memory since the log will have errors about the amount
        of social assets connected and the last activities. To fix this problem the social asset is then deactivated
        harshly, that means the social asset will have no storage, nor items, nor route, not destination distance and
        will not be active."""

        self.is_active = False
        self.last_action_result = False
        self.physical_storage = 0
        self.virtual_storage = 0
        self.destination_distance = 0
        self.route.clear()
        self.physical_storage_vector.clear()
        self.virtual_storage_vector.clear()
