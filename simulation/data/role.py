# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Role.java

class Role:

	def __init__(self, identifier, config):
		self.speed = config['roles'][identifier]['speed']
		self.physical_capacity = config['roles'][identifier]['capacity_physical']
		self.virtual_capacity = config['roles'][identifier]['capacity_virtual']
		self.battery = config['roles'][identifier]['battery']
		self.abilities = config['roles'][identifier]['abilities']
		self.perceive = config['roles'][identifier]['perceive']
		self.roads = config['roles'][identifier]['kind']





























