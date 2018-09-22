# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java

class ActionExecutor:

    def __init__(self, config):
        self.a = 'a'

    def execute(self, agent, command):
        action = 'a'
        parameters = 'a' 

        if action == None:
            agent.last_action_result = False
            pass #log(failed_no_action)

        elif action == 'move':
            if parameters.size() < 1 or parameters.size() > 2:
                    pass #log(failed_wrong_param)
            else:        
                try:
                    if parameters.size() == 1:
                        facility = parameters[0]
                        try:
                            if(agent.route == None):
                                try:
                                    route = world_map.create_route_facility(agent.role.location, facility) #not implemented yet
                                    agent.route = route
                                except:
                                    pass #log(failed_unknown_facility)
                            else: 
                                agent.location = agent.route.next_node() #not implemented yet
                        except:
                            pass #log(failed_no_route)
                    elif parameters.size() == 2:
                        latitude = parameters[0]
                        longitude = parameters[1]
                        try:
                            agent.location = [latitude, longitude]
                        except:
                            pass #log(failed_no_route)
                except:
                    pass #log(failed)


        elif action == 'deliver_physical':
            if parameters.size() < 1 or parameters.size() > 2:
                pass#log(failed_wrong_param)
            else:
                try:
                    if parameters.size() == 1:
                        agent_deliver(agent, parameters[0])
                    elif parameters.size() == 2:
                        agent_deliver(agent, parameters[0], parameters[1])
                except:
                    pass#log(failed)

        elif action == 'deliver_virtual':
            if parameters.size() < 1 or parameters.size() > 2:
                    pass#log(failed_wrong_param)    
            else:
                try:
                    if parameters.size() == 1:
                        agent_deliver('virtual', parameters[0])
                    elif parameters.size() == 2:
                        agent_deliver('virtual', parameters[0], parameters[1])
                except:
                    pass#log(failed)


        elif action == 'charge':
            if parameters.size() > 0:
                pass#log(failed_wrong_param)
            else:
                try:
                    facility = world_map.get_facility(agent.location) #not implemented yet        
                    if facility.id == 'cdm':
                        cdm.charge(agent) #not implemented yet
                    else:
                        pass#log(failed_location)
                except:
                    pass#log(failed)


        elif action == 'rescue_victim':
            if parameters.size() > 1:
                pass#log(failed_wrong_param)
            else:
                try:
                    victim = world_map.search_victim(parameters[0]) #not implemented yet
                    if victim == None:
                        pass#log(failed_unknown_item)
                    if victim.location == agent.location:
                        world_map.remove_victim(victim) #not implemented yet
                    else:
                        pass#log(failed_location)
                    weight = victim.get_weight() #not implemented yet
                    try:
                        agent.add_physical_item(victim.get_name())
                    except:
                        pass#log(failed_capacity)
                except:
                    pass#log(failed)    


        elif action == 'collect_water':
            if parameters.size() > 0:
                pass#log(failed_wrong_param)
            else:
                try:
                    facility = world_map.get_facility(agent.location) #not implemented yet
                    if facility.id == 'water':
                        try:
                            #create sample of water
                            agent.add_physical_item(water)
                        except:
                            pass#log(failed_capacity)
                    else:
                        pass#log(failed_location)
                except:
                    pass#log(failed)


        elif action == 'photograph':
            if parameters.size() > 0:
                pass#log(failed_wrong_param)
            else:
                try:
                    facility = world_map.get_facility(agent.location) #not implemented yet
                    if facility.id == 'photo':
                        try:
                            #create photo
                            agent.add_virtual_item(photo)
                        except:
                            pass#log(failed_capacity)
                    else:
                        pass#log(failed_location)
                except:
                    pass#log(failed)


        elif action == 'search_social_asset':
            if parameters.size() != 1 or parameters.size != 3:
                pass#log(failed_wrong_param)
            else:
                try:
                    if parameters.size() == 1:
                        assets = world_map.search_social_asset(radius, agent.location) #not implemented yet
                        #show assets to agent
                    else:
                        assets = world_map.search_social_asset(radius, latitude, longitude) #not implemented yet
                        #show assets to agent
                except:
                    pass#log(failed)


        elif action == 'analyze_photo':
            if parameters.size() > 0:
                pass#log(failed_wrong_param)
            else:
                try:
                    if agent.virtual_storage != agent.role.virual_capacity:
                        agent.remove_virtual_item('photo')
                    else:
                        pass#log(failed_item_amount)
                except:
                    pass#log(failed)


        else:
            pass#log(failed)


    def agent_deliver(self, agent, kind, amount = None):
        total_removed = 0
        if amount == None:
            try:
                if kind == 'physical':
                    total_removed = agent.remove_physical_item('physical')
                elif kind == 'virtual':
                    total_removed = agent.remove_virtual_item('virtual')
                else:
                    pass#log(failed_invalid_kind)
            except:
                pass#log(failed_unknown_item)
            try:
                cdm.deliver(agent, kind, total_removed) #not implemented yet
            except:
                pass#log(failed_location)
        elif amount != None:
            try:
                verify(amount) #not implemented yet
            except:
                pass#log(failed_item_amount)
            try:
                if kind == 'physical':
                    total_removed = agent.remove_physical_item('physical', amount)
                elif kind == 'virtual':
                    total_removed = agent.remove_virtual_item('virtual', amount)
            except:
                pass#log(failed_unknown_item)
            try:
                cdm.deliver(agent, kind, total_removed) #not implemented yet
            except:
                pass#log(failed_location)

