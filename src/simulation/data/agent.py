# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java
from src.simulation.exceptions import *
from src.simulation.data.events.flood import *
from src.simulation.data.events.victim import *
from src.simulation.data.events.photo import *

class Agent:

    def __init__(self, id, role):
        """
        [Object that represents an instance of an agents 'controller',
        responsible for the manipulation of all its perceptions]

        :param id: 'Manipulated' agent's id.
        :param role: The agent's main function over the simulation,
        which covers its skills and limitations.
        """

        self.id = id
        self.role = role
        self.last_action = None
        self.last_action_result = False
        self.location = [0, 0]
        self.route = None
        self.physical_storage = role.physical_capacity
        self.virtual_storage = role.virtual_capacity
        self.physical_storage_vector = []
        self.virtual_storage_vector = []

    def __repr__(self):
        return str(self.id) + ' - ' +  str(self.role)

    def discharge(self):
        """
        [Changes the agent's battery to zero.]
        """

        self.role.actual_battery = 0

    def charge(self):
        """
        [Changes the agent's battery to its full charge capacity.]
        """

        self.role.actual_battery = self.role.total_battery

    def add_physical_item(self, item, amount=None):
        """
        [Add a certain physical item to the agent's physical storage.
        The agent's current 'free space' is reduced by the item's size.]

        :param item: The physical item to be stored.
        :param amount: The amount of the specified item to be stored.
        In case it is not specified, only one sample is stored.
        """

        size = item.size

        # if amount != None:
        #     if size * amount < self.physical_storage:
        #         self.physical_storage -= size * amount
        #         e = 0
        #         while e < amount:
        #             self.physical_storage_vector.append(item)
        #             e += 1
        #     else:
        #         raise Failed_capacity('The agent does not have enough physical storage.')
        # else:
        if size > self.virtual_storage:
            raise Failed_capacity('The agent does not have enough physical storage.')

        self.physical_storage -= size
        self.physical_storage_vector.append(item)

    def add_virtual_item(self, item, amount=None):
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

        # if amount != None:
        #     if size * amount < self.virtual_storage:
        #         self.virtual_storage -= size * amount
        #         e = 0
        #         while e < amount:
        #             self.virtual_storage_vector.append(item)
        #             e += 1
        #     else:
        #         raise Failed_capacity('The agent does not have enough virtual storage.')
        # else:
        if size > self.virtual_storage:
            raise Failed_capacity('The agent does not have enough physical storage.')

        self.virtual_storage -= size
        self.virtual_storage_vector.append(item)

    def remove_physical_item(self, item, amount=None):
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

        if self.virtual_storage == self.role.virual_capacity:
            raise Failed_item_amount('The agents has no victims or water samples to deliver.')

        if not self.virtual_storage_vector.contains(item):
            raise Failed_unknown_item('No physical item with this ID is storaged.')

        removed = []

        if amount == None:
            removed = self.remove(self.physical_storage_vector, item)
        else:
            removed = self.remove(self.physical_storage_vector, item, amount)
            
        for e in removed:
            self.physical_storage += e.size

        return removed

    def remove_virtual_item(self, item, amount=None):
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

        if self.virtual_storage == self.role.virual_capacity:
            raise Failed_item_amount('The agents has no photos to deliver.')

        if not self.virtual_storage_vector.contains(item):
            raise Failed_unknown_item('No virtual item with this ID is storaged.')

        removed = []

        if amount == None:
            removed = self.remove(self.virtual_storage_vector, item)
        else:
            removed = self.remove(self.virtual_storage_vector, item, amount)

        for e in removed:
            self.virtual_storage += e.size

        return removed

    def remove(self, lst, item, amount=None):
        """
        [Agent's auxiliary method for generic type item removal.]

        :param lst: A list containing all the current items
        of the agent's specified kind storage (physical or virtual).
        :param item: The type of the item to be removed.
        :param removed: A list that will aggregate all removed instances
        of the specified item.
        :param amount: The amount of the parametrized item to be removed.
        :return: Returns a list containing all the removed items.
        """

        if amount == None:
            amount = len(lst)

        removed = []

        for e in range(len(lst)):
            if amount == 0:
                break
            
            if lst[e].type == item:
                removed.append(lst[e])
                lst[e] = None
                amount -= 1

        lst = [e for e in lst if e != None]

        return removed

        