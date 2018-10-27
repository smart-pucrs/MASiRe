# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java
from src.simulation.exceptions import *
class Agent:

    # constructor with agent's private attributes
    def __init__(self, identifier, role):
        self.role = role
        self.identifier = identifier
        self.last_action = None
        self.last_action_result = False
        self.location = [0, 0]
        self.route = None
        self.physical_storage = role.physical_capacity
        self.virtual_storage = role.virtual_capacity
        self.physical_storage_vector = []
        self.virtual_storage_vector = []

    def __repr__(self):
        return str(self.identifier) + ' - ' +  str(self.role)

    def discharge(self):
        self.role.actual_battery = 0

    def charge(self):
        self.role.actual_battery = self.role.total_battery

    def add_physical_item(self, item, amount=None):

        size = item.size

        if amount != None:
            if size * amount < self.physical_storage:
                self.physical_storage -= size * amount
                e = 0
                while e < amount:
                    self.physical_storage_vector.append(item)
                    e += 1
            else:
                raise Failed_capacity('The agent does not have enough physical storage.')
        else:
            self.virtual_storage_vector.append(item)
            self.virtual_storage -= size

    def add_virtual_item(self, item, amount=None):

        size = item.size

        if amount != None:
            if size * amount < self.virtual_storage:
                self.virtual_storage -= size * amount
                e = 0
                while e < amount:
                    self.virtual_storage_vector.append(item)
                    e += 1
            else:
                raise Failed_capacity('The agent does not have enough virtual storage.')
        else:
            self.virtual_storage_vector.append(item)
            self.virtual_storage -= size



    def remove_physical_item(self, item, amount=None):

        removed = []

        if self.virtual_storage == self.role.virual_capacity:
            raise Failed_item_amount('The agents has no victims or water samples to deliver.')

        if not self.virtual_storage_vector.contains(item):
            raise Failed_unknown_item('No physical item with this ID is storaged.')

        vector = self.physical_storage_vector

        if amount == None:
            removed = self.remove(vector, item, vector.size()-1, [])
            print(removed)
            self.physical_storage = self.role.physical_capacity
        else:
            removed = self.remove(vector, item, amount, [])
            print(removed)
            for e in removed:
                self.physical_storage += e.size()

        return len(removed)

    def remove_virtual_item(self, item, amount=None):

        removed = []

        if self.virtual_storage == self.role.virual_capacity:
            raise Failed_item_amount('The agents has no photos to deliver.')

        if not self.virtual_storage_vector.contains(item):
            raise Failed_unknown_item('No virtual item with this ID is storaged.')

        vector = self.virtual_storage_vector

        if amount == None:
            removed = self.remove(vector, item, vector.size()-1, [])
            print(removed)
            self.virtual_storage = self.role.physical_capacity
        else:
            removed = self.remove(vector, item, amount, [])
            print(removed)
            for e in removed:
                self.virtual_storage += e.size()

        return len(removed)

    def remove(self, lst, item, removed, amount=None):
        for e in range(0,len(lst)):
            if amount == 0:
                return removed
            if lst[e].id == item:
                aux_item = lst[e]
                lst[e] = lst[lst.size() - 1]
                lst[lst.size() - 1] = aux_item
                removed.append(lst.pop())
                amount = amount - 1