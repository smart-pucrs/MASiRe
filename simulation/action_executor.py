# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java

class ActionExecutor:

 	def __init__(self, config):
 		self.a = 'a'

 	def parse_action():
 		#parses the action in a string of commands

 	def parse_parameters():
 		#parses the parameters of an action

 	def execute(self, agent, command):
 		action = parse_action(command)
 		parameters = parse_parameters(command) 

 		if action is None:
 			agent.last_action_result = False
 			#log(failed_no_action)

 		elif action is 'move':
 			if parameters.size() < 1 or parameters.size() > 2:
	 				#log(failed_wrong_param)
	 		else:		
	 			try:
		 			if parameters.size() == 1:
		 				facility = parameters[0]
		 				try:
		 					if(agent.route is None):
		 						try:
		 							route = _map.create_route_facility(agent.role.location, facility) #not implemented yet
		 							agent.route = route
		 						except:
		 							#log(failed_unknown_facility)
		 					else: 
		 						agent.location = agent.route.next_node() #not implemented yet
		 				except:
		 					#log(failed_no_route)
		 			elif parameters.size() == 2:
		 				latitude = parameters[0]
		 				longitude = parameters[1]
		 				try:
		 					agent.location = [latitude, longitude]
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
		 				agent_deliver(agent, parameters[0])
		 			elif parameters.size() == 2:
		 				agent_deliver(agent, parameters[0], parameters[1])
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
 					facility = _map.get_facility(agent.location) #not implemented yet		
 					if facility.id is 'cdm':
 						cdm.charge(agent) #not implemented yet
 					else:
 						#log(failed_location)
 				except:
 					#log(failed)


 		elif action is 'rescue_victim':
 			if parameters.size() > 1:
 				#log(failed_wrong_param)
 			else:
 				try:
					victim = _map.search_victim(parameters[0]) #not implemented yet
 					if victim is None:
 						#log(failed_unknown_item)
 					if victim.location is agent.location
 						_map.remove_victim(victim) #not implemented yet
 					else:
 						#log(failed_location)
 					weight = victim.get_weight() #not implemented yet
 					try:
 						agent.add_physical_item(victim.get_name())
 					except:
 						#log(failed_capacity)
 				except:
 					#log(failed)	


 		elif action is 'collect_water':
		 	if parameters.size() > 0:
		 		#log(failed_wrong_param)
		 	else:
		 		try:
		 			facility = _map.get_facility(agent.location) #not implemented yet
		 			if facility.id = 'water':
		 				try:
		 					#create sample of water
		 					agent.add_physical_item(water)
		 				except:
		 					#log(failed_capacity)
		 			else:
		 				#log(failed_location)
		 		except:
		 			#log(failed)


 		elif action is 'photograph':
 			if parameters.size() > 0:
 				#log(failed_wrong_param)
 			else:
 				try:
 					facility = _map.get_facility(agent.location) #not implemented yet
 					if facility.id = 'photo':
 						try:
 							#create photo
 							agent.add_virtual_item(photo)
 						except:
 							#log(failed_capacity)
 					else:
 						#log(failed_location)
 				except:
 					#log(failed)


 		elif action is 'search_social_asset':
 			if parameters.size() != 1 or parameters.size != 3:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if parameters.size() == 1:
 						assets = _map.search_social_asset(radius, agent.location) #not implemented yet
 						#show assets to agent
 					else:
 						assets = _map.search_social_asset(radius, latitude, longitude) #not implemented yet
 						#show assets to agent
 				except:
 					#log(failed)


 		elif action is 'analyze_photo':
 			if parameters.size() > 0:
 				#log(failed_wrong_param)
 			else:
 				try:
 					if agent.virtual_storage is not agent.role.virual_capacity:
 						agent.remove_virtual_item('photo')
 					else:
 						#log(failed_item_amount)
 				except:
 					#log(failed)


 		else:
 			#log(failed)


 	def agent_deliver(self, agent, kind, amount = None):
		total_removed = 0
	 	if amount is None:
	 		try:
	 			if kind is 'physical':
	 				total_removed = agent.remove_physical_item('physical')
	 			elif kind is 'virtual':
	 				total_removed = agent.remove_virtual_item('virtual')
	 			else:
	 				#log(failed_invalid_kind)
	 		except:
	 			#log(failed_unknown_item)
	 		try:
	 			cdm.deliver(agent, kind, total_removed) #not implemented yet
	 		except:
	 			#log(failed_location)
	 	elif amount is not None:
	 		try:
	 			verify(amount) #not implemented yet
	 		except:
	 			#log(failed_item_amount)
	 		try:
	 			if kind is 'physical':
	 				total_removed = agent.remove_physical_item('physical', amount)
	 			elif kind is 'virtual':
	 				total_removed = agent.remove_virtual_item('virtual', amount)
	 		except:
	 			#log(failed_unknown_item)
	 		try:
	 			cdm.deliver(agent, kind, total_removed) #not implemented yet
	 		except:
	 			#log(failed_location)

