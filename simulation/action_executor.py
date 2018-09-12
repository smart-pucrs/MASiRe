# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java

class ActionExecutor:

 	def __init__(self, config):
 		self.a = 'a'

 	def parse_action():
 		#parses the action in a string of commands

 	def parse_parameters():
 		#parses the parameters of an action

 	def execute(agent, command):
 		action = parse_action(command)
 		parameters = parse_parameters(command) 

 		if action is None:
 			agent.set_last_action_result(False)
 			#log(failed_no_action)

 		elif action is 'move':
 			if parameters.size() < 1 or parameters.size() > 2:
	 				#log(failed_wrong_param)
	 		else:		
	 			try:
		 			if parameters.size() == 1:
		 				facility = parameters[0]
		 				try:
		 					if(agent.get_route is None):
		 						try:
		 							route = create_route_facility(agent.get_location, facility)
		 							agent.set_route(route)
		 						except:
		 							#log(failed_unknown_facility)
		 					else: 
		 						agent.set_route(agent.get_route().get_next_node())
		 				except:
		 					#log(failed_no_route)
		 			elif parameters.size() == 2:
		 				latitude = parameters[0]
		 				longitude = parameters[1]
		 				try:
		 					route.create_route_location(agent.get_location, latitude, longitude)
		 				except:
		 					#log(failed_no_route)
 				except:
 					#log(failed)


 		elif action is 'deliver_physical':
	 		if parameters.size() < 1 or parameters.size() > 2:
	 			#log(failed_wrong_param)
	 		else:
	 			try:
		 			if parameters.size() == 1:
		 				agent_deliver('pyshical', parameters[0])
		 			elif parameters.size() == 2:
		 				agent_deliver('physical', parameters[0], parameters[1])
	 			except:
	 				#log(failed)

 		elif action is 'deliver_virtual':
 			if parameters.size() < 1 or parameters.size() > 2:
		 			#log(failed_wrong_param)	
 			else:
				try:
		 			if parameters.size() == 1:
		 				agent_deliver('virtual', parameters[0])
		 			elif parameters.size() == 2:
		 				agent_deliver('virtual', parameters[0], parameters[1])
		 		except:
	 				#log(failed)


 		elif action is 'charge':
 			if parameters.size() > 0:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if check_cdm_location(agent.get_location): #not implemented yet
 						agent.charge()
 					else:
 						#log(failed_location)
 				except:
 					#log(failed)


 		elif action is 'rescue_victim':
 			if parameters.size() > 1:
 				#log(failed_wrong_param)
 			else:
 				try:
					victim = search_victim(parameters[0]) #not implemented yet
 					if victim is None:
 						#log(failed_unknown_item)
 					try:
 						victim.rescue_victim()
 					except:
 						#log(failed_location)
 					weight = victim.get_weight()
 					if agent.get_free_physical_capacity() > victim.get_weight():
 						agent.add_physical_item(victim.get_name(), weight)
 					else:
 						#log(failed_capacity)
 				except:
 					#log(failed)	


 		elif action is 'collect_water':
		 	if parameters.size() > 0:
		 		#log(failed_wrong_param)
		 	else:
		 		try:
		 			if agent.get_free_physical_capacity() > 0: #?
		 				try:
		 					water.collect(agent) #not implemented yet
		 				except:
		 					#log(failed_location)
		 			else:
		 				#log(failed_capacity)
		 		except:
		 			#log(failed)


 		elif action is 'photograph':
 			if parameters.size() > 0:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if agent.get_free_virtual_capacity() > 0: #?
 						try:
 							role.get_photograph(agent.get_location()) #not implemented yet
 							agent.add_virtual_item('photo') # photo_1, 2, 3 ... (?) - amount?
 						except:
 							#log(failed_location)
 					else:
 						#log(failed_capacity)
 				except:
 					#log(failed)


 		elif action is 'search_social_asset':
 			if parameters.size() != 1 or parameters.size != 3:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if parameters.size() == 1:
 						_map.search_social_asset(radius) #not implemented yet - agent location(?)
 					else:
 						_map.search_social_asset(radius, latitude, longitude) #not implemented yet - agent location(?)
 				except:
 					#log(failed)


 		elif action is 'analyze_photo':
 			if parameters.size() > 0:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if agent.get_free_virtual_capacity() == agent.get_initial_virtual_capacity():
 						success = world.analyze() #not implemented yet (world?)
 						if success:
 							agent.remove_virtual_item('photo') #photo_1, 2,3 ... (?) - amount?
 					else:
 						#log(failed_item_amount)
 				except:
 					#log(failed)


 		else:
 			#log(failed)


 	def agent_deliver(self, kind, item, amount = None):
	 	if amount is None:
	 		try:
	 			if kind is 'physical':
	 				agent.remove_physical_item(item)
	 			elif kind is 'virtual':
	 				agent.remove_virtual_item(item)
	 			else:
	 				#log(failed_invalid_kind)
	 				raise Exception('invalid kind for delivery')
	 		except:
	 			#log(failed_unknown_item)
	 		try:
	 			cdm.deliver(item) #not implemented yet
	 		except:
	 			#log(failed_location)
	 	elif amount is not None:
	 		try:
	 			verify(amount)#not implemented yet
	 		except:
	 			#log(failed_item_amount)
	 		try:
	 			if kind is 'physical':
	 				agent.remove_physical_item(name)
	 			elif kind is 'virtual':
	 				agent.remove_virtual_item(name)
	 		except:
	 			#log(failed_unknown_item)
	 		try:
	 			cdm.deliver(item, amount) #not implemented yet
	 		except:
	 			#log(failed_location)

