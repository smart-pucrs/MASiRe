# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java

from simulation.exceptions.exceptions import *


class Agent:

    def __init__(self, agent_token, role, role_name, cdm_location, agent_info):
        """
        [Object that represents an instance of an agents 'controller',
        responsible for the manipulation of all its perceptions]

        :param agent_token: 'Manipulated' agent's id.
        :param role: The agent's main function over the simulation,
        which covers its skills and limitations.
        """
        self.token = agent_token
        self.last_action = 'pass'
        self.last_action_result = True
        self.location = cdm_location
        self.route = []
        self.physical_storage_vector = []
        self.virtual_storage_vector = []
        self.is_active = True
        self.social_assets = []
        self.role = role_name
        self.physical_storage = role.physical_capacity
        self.virtual_storage = role.virtual_capacity
        self.virtual_capacity = role.virtual_capacity
        self.physical_capacity = role.physical_capacity
        self.actual_battery = role.battery
        self.max_charge = role.battery
        self.speed = role.speed
        self.destination_distance = 0
        self.abilities = role.abilities
        self.agent_info = agent_info

    def discharge(self):
        """
        [Changes the agent's battery to zero.]
        """
        if self.destination_distance:
            self.actual_battery = self.actual_battery - int(self.speed / 5) \
                if self.actual_battery - self.speed / 5 \
                else 0

    def check_battery(self):
        return self.actual_battery - int(self.speed / 5) if self.actual_battery - self.speed / 5 else 0

    def charge(self):
        """
        [Changes the agent's battery to its full charge capacity.]
        """

        self.actual_battery = self.max_charge

    def add_physical_item(self, item):
        """
        [Add a certain physical item to the agent's physical storage.
        The agent's current 'free space' is reduced by the item's size.]

        :param item: The physical item to be stored.
        :param amount: The amount of the specified item to be stored.
        In case it is not specified, only one sample is stored.
        """

        size = item.size
        if size > self.physical_storage:
            raise Failed_capacity('The agent does not have enough physical storage.')

        self.physical_storage -= size
        self.physical_storage_vector.append(item)

    def add_virtual_item(self, item):
        """
        [Add a certain parametrized virtual item to the agent's virtual storage.
        The agent's current 'free space' is reduced by the item's size.
        In case the agent's physical storage can't support the item's size, an
        error is thrown.]

        :param item: The virtual item to be stored.
        :param amount: The amount of the specified item to be stored.
        In case it is not specified, only one sample is stored.
        """

        size = item.size
        if size > self.virtual_storage:
            raise Failed_capacity('The agent does not have enough physical storage.')

        self.virtual_storage -= size
        self.virtual_storage_vector.append(item)

    def remove_physical_item(self, item, amount=1):
        """
        [Removes a certain parametrized physical item from the agent's physical storage.
        The agent's current 'free physical space' is increased by the item's size.
        In case the agent's physical storage does not contains the specified item,
        an error is thrown.]

        :param item: The physical item to be removed.
        :param amount: The amount of the specified item to be removed.
        In case it is not specified, every instance of the item contained
        in the agent's physical storage is removed.
        :return: A list containing all the removed items.
        """

        if self.physical_storage == self.physical_capacity:
            raise Failed_item_amount('The agents has no victims or water samples to deliver.')

        found_item = False
        removed = []
        for stored_item in self.physical_storage_vector:
            if item == stored_item.type and amount:
                found_item = True
                removed.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise Failed_unknown_item('No physical item with this ID is stored.')

        for removed_item in removed:
            self.physical_storage_vector.remove(removed_item)
            self.physical_storage += removed_item.size

        return removed

    def remove_virtual_item(self, item, amount=1):
        """
        [Removes a certain parametrized virtual item from the agent's virtual storage.
        The agent's current 'free virtual space' is increased by the item's size.
        In case the agent's virtual storage does not contains the specified item,
        an error is thrown.]

        :param item: The virtual item to be removed.
        :param amount: The amount of the specified item to be removed.
        In case it is not specified, every instance of the item contained
        in the agent's virtual storage is removed.
        :return: A list containing all the removed items.
        """

        if self.virtual_storage == self.virtual_capacity:
            raise Failed_item_amount('The agents has no photos to deliver.')

        found_item = False
        removed = []
        for stored_item in self.virtual_storage_vector:

            if item == stored_item.type and amount:
                found_item = True
                removed.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise Failed_unknown_item('No virtual item with this ID is stored.')

        for removed_item in removed:
            self.virtual_storage_vector.remove(removed_item)
            self.virtual_storage += removed_item.size

        return removed

    def json(self):
        copy = self.__dict__.copy()
        del copy['agent_info']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        copy['route'] = [{'lat': position[0], 'lon': position[1]} for position in copy['route']]
        return copy

    def variables_json(self):
        copy = self.__dict__.copy()
        del copy['agent_info']
        del copy['abilities']
        del copy['max_charge']
        del copy['physical_capacity']
        del copy['role']
        del copy['speed']
        del copy['virtual_capacity']
        del copy['token']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        copy['route'] = [{'lat': position[0], 'lon': position[1]} for position in copy['route']]
        return copy

    def constants_json(self):
        copy = self.__dict__.copy()
        del copy['agent_info']
        del copy['actual_battery']
        del copy['is_active']
        del copy['physical_storage']
        del copy['physical_storage_vector']
        del copy['virtual_storage']
        del copy['virtual_storage_vector']
        del copy['last_action']
        del copy['last_action_result']
        del copy['location']
        del copy['route']
        del copy['social_assets']
        return copy
