# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java

class Agent:

#constructor with agent's private attributes
	def __init__ (self, identifier, role):
		self.role = role
		self.identifier = identifier 
		self.last_action = None
		self.last_action_result = True
		self.location = [0,0]
		self.route = None
		self.physical_storage = role.physical_capacity
		self.virtual_storage = role.virtual_capacity
		self.physical_storage_vector = []
		self.virtual_storage_vector = []

	def __repr__(self):
		return str(self.id) + ' - ' + self.role

	def discharge(self):
		self.role.actual_battery = 0

	def charge(self):
		self.role.actual_battery = role.total_battery

	def add_physical_item(self, item, amount=None):

		weight = item.get_weight()
		if weight < self.physical_storage:
			if amount is not None:
				if weight*amount < self.physical_storage:
					self.physical_storage -= weight*amount
					while e < amount:
						self.virtual_storage_vector.append(item)
						e+=1
			else:
				self.physical_storage_vector.append(item)
				self.physical_storage -= weight

		else:
			raise Failed_capacity('The agent does not have enough physical storage.')

	def add_virtual_item(self, item, amount=None):

		size = item.get_size()
		if size < self.virtual_storage:
			if amount is not None:
				if size*amount < self.virtual_storage:
					self.virtual_storage -= size*amount
					while e < amount:
						self.virtual_storage_vector.append(item)
						e+=1
			else:
				self.virtual_storage_vector.append(item)
				self.virtual_storage -= size

		else:
			raise Failed_capacity('The agent does not have enough virtual storage.')
		
			
	def remove_physical_item(self, item, amount=None):

		if self.virtual_storage is self.role.virual_capacity:
			raise Failed_item_amount('The agents has no victims to deliver.')

		if !self.virtual_storage_vector.contains(item):
			raise Failed_unknown_item('No physical item with this ID is storaged.')

		vector = self.physical_storage_vector

		if amount is None:
			removed = remove(vector, item, vector.size(), [])
			#print(removed)
			self.physical_storage = self.role.physical_capacity
		else:
			removed = remove(vector, item, amount, [])
			#print(removed)
			for e in removed:
				self.physical_storage += removed.get_weight()


	def remove_virtual_item(self, item, amount=None):

		if self.virtual_storage is self.role.virual_capacity:
			raise Failed_item_amount('The agents has no photos to deliver.')

		if !self.virtual_storage_vector.contains(item):
			raise Failed_unknown_item('No virtual item with this ID is storaged.')

		vector = self.virtual_storage_vector

		if amount is None:
			removed = remove(vector, item, vector.size(), [])
			#print(removed)
			self.virtual_storage = self.role.physical_capacity
		else:
			removed = remove(vector, item, amount, [])
			#print(removed)
			for e in removed:
				self.virtual_storage += removed.get_size()


	def remove(self, lst, item, removed, amount=None):
		if amount == 0:
			return removed
		for e in lst:
			if lst[e].id is item.id:
				aux_item = lst[e]
				lst[e] = lst[lst.size()-1]
				lst[lst.size()-1] = aux_item
				amount = amount - 1
				remove(self, lst, item, removed.append(lst.pop()), amount)







