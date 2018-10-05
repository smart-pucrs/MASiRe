# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Role.java

class Role:

	def __init__(self, id, config):
		self.id = id
		self.roads = config['roles'][id]['kind']
		self.speed = config['roles'][id]['speed']
		self.battery = config['roles'][id]['battery']
		self.percieve = config['roles'][id]['percieve']
		self.abilities = config['roles'][id]['abilities']
		self.virtual_capacity = config['roles'][id]['capacity_virtual']
		self.physical_capacity = config['roles'][id]['capacity_physical']





























