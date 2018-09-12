# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java

class Agent:

	last_action = 'None'
	last_action_result = True
	location = [0,0]
	route = None
	physical_storage = []
	virtual_storage = []

#constructor with agent's private attributes
	def __init__ (self, identifier, kind):
		self.identifier = identifier 
		self.kind = kind

#getters
	def get_identifier():
		return self.identifier
	def get_kind():
		return self.kind
	def get_skills():
		return self.skills
	def get_battery():
		return self.battery
	def get_speed():
		return self.speed
	def get_location():
		return self.location
	def get_free_physical_capacity():
		return self.physical_capacity
	def get_free_virtual_capacity():
		return self.virtual_capacity
	def get_initial_physical_capacity():
		return self.initial_physical_capacity
	def get_initial_virtual_capacity():
		return self.initial_virtual_capacity
	def get_last_action():
		return last_action
	def get_last_action_result():
		return self.last_action_result
	def get_route():
		return self.route
	def remove_physical_item(item):
		#self.physical_storage += amount (?)
		self.physical_storage.remove(item)
		return #(?)
	def remove_virtual_item(item):
		#self.virtual_storage += amount (?)
		self.virtual_storage.remove(item)
		return #(?)
#setters
	def set_skills(skills):
		self.skills = skills
	
	def discharge():
		self.battery = 0

	def charge(amount):
		self.battery = total_battery

	def set_battery(amount):
		self.total_battery = amount

	def set_speed(speed):
		self.speed = speed

	def set_location(x, y):
		location[0] = x
		location[1] = y

	def set_free_physical_capacity(space):
		self.initial_physical_capacity = space
		self.physical_capacity = space

	def set_free_virtual_capacity(space):
		self.initial_virtual_capacity = space
		self.virtual_capacity = space

	def set_last_action(action):
		self.last_action = action

	def set_last_action_result(value):
		self.last_action_result = value

	def set_route(Route route):
		self.route = route

	def add_physical_item(item, amount=None):
		self.physical_storage.append(item)
		if amount is not None:
			self.physical_capacity -= amount

	def add_virtual_item(item, amount=None):
		self.virtual_storage.append(item)
		if amount is not None:
			self.virtual_capacity -= amount

