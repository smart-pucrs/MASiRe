def parse_action(action):
    return ''

def parse_parameters(command):
    return ''  # parses the parameters of an action


class ActionExecutor:

    def __init__(self, config):
        self.a = 'a'

    def execute(self, agent, command, action):
        parameters = parse_parameters(command)

        if action is None:
            agent.set_last_action_result(False)
            print 'failed_no_action'

        elif action is 'move':
            if parameters.size() < 1 or parameters.size() > 2:
                print 'failed_wrong_param'
            else:
                try:
                    if parameters.size() == 1:
                        facility = parameters[0]
                        try:
                            if agent.get_route is None:
                                try:
                                    route = self.create_route_facility(agent.get_location, facility)
                                    agent.set_route(route)
                                except:
                                    print 'failed_unknown_facility'
                            else:
                                agent.set_route(agent.get_route().get_next_node())
                        except:
                            print 'failed_no_route'
                    elif parameters.size() == 2:
                        latitude = parameters[0]
                        longitude = parameters[1]
                        try:
                            pass
                        # route.create_route_location(agent.get_location, latitude, longitude)
                        except:
                            print 'failed_no_route'
                except:
                    print 'failed'


        elif action is 'deliver_physical':
            if parameters.size() < 1 or parameters.size() > 2:
                print 'failed_wrong_param'
            else:
                try:
                    self.agent_deliver('pyshical', *parameters)
                except:
                    print 'failed'

        elif action is 'deliver_virtual':
            if parameters.size() < 1 or parameters.size() > 2:
                print 'failed_wrong_param'
            else:
                try:
                    self.agent_deliver('virtual', *parameters)
                except:
                    print 'failed'


        elif action is 'charge':
            if parameters.size() > 0:
                print 'failed_wrong_param'
            else:
                try:
                    if self.check_cdm_location(agent.get_location):  # not implemented yet
                        agent.charge()
                    else:
                        print 'failed_location'
                except:
                    print 'failed'


        elif action is 'rescue_victim':
            if parameters.size() > 1:
                print 'failed_wrong_param'
            else:
                try:
                    victim = self.search_victim(*parameters)  # not implemented yet
                    if victim is None:
                        print 'failed_unknown_item'
                    try:
                        victim.rescue_victim()
                    except:
                        print 'failed_location'
                    weight = victim.get_weight()
                    if agent.get_free_physical_capacity() > victim.get_weight():
                        agent.add_physical_item(victim.get_name(), weight)
                    else:
                        print 'failed_capacity'
                except:
                    print 'failed'


        elif action is 'collect_water':
            if parameters.size() > 0:
                print 'failed_wrong_param'
            else:
                try:
                    if agent.get_free_physical_capacity() > 0:  # ?
                        try:
                            pass
                        # water.collect(agent)  # not implemented yet
                        except:
                            print 'failed_location'
                    else:
                        print 'failed_capacity'
                except:
                    print 'failed'


        elif action is 'photograph':
            if parameters.size() > 0:
                print 'failed_wrong_param'
            else:
                try:
                    if agent.get_free_virtual_capacity() > 0:  # ?
                        try:
                            # role.get_photograph(agent.get_location())  # not implemented yet
                            agent.add_virtual_item('photo')  # photo_1, 2, 3 ... (?) - amount?
                        except:
                            print 'failed_location'
                    else:
                        print 'failed_capacity'
                except:
                    print 'failed'


        elif action is 'search_social_asset':
            if parameters.size() != 1 or parameters.size != 3:
                print 'failed_wrong_param'
            else:
                try:
                    if parameters.size() == 1:
                        pass
                    # _map.search_social_asset(radius)  # not implemented yet - agent location(?)
                    else:
                        pass
                        # map.search_social_asset(radius, latitude, longitude)  # not implemented yet - agent location(?)
                except:
                    print 'failed'


        elif action is 'analyze_photo':
            if parameters.size() > 0:
                print 'failed_wrong_param'
            else:
                try:
                    if agent.get_free_virtual_capacity() == agent.get_initial_virtual_capacity():
                        success = True  # world.analyze()  # not implemented yet (world?)
                        if success:
                            agent.remove_virtual_item('photo')  # photo_1, 2,3 ... (?) - amount?
                    else:
                        print 'failed_item_amount'
                except:
                    print 'failed'


        else:
            print 'failed'

    def agent_deliver(self, kind, item, amount=None):
        if amount is None:
            try:
                if kind is 'physical':
                    pass
                # agent.remove_physical_item(item)
                elif kind is 'virtual':
                    pass
                # agent.remove_virtual_item(item)
                else:
                    print 'failed_invalid_kind'
                    raise Exception('invalid kind for delivery')
            except:
                print 'failed_unknown_item'
            try:
                pass
            # cdm.deliver(item)  # not implemented yet
            except:
                print 'failed_location'
        elif amount is not None:
            try:
                pass
            # verify(amount)  # not implemented yet
            except:
                print 'failed_item_amount'
            try:
                if kind is 'physical':
                    pass
                # agent.remove_physical_item(name)
                elif kind is 'virtual':
                    pass
                # agent.remove_virtual_item(name)
            except:
                print 'failed_unknown_item'
            try:
                pass
            # cdm.deliver(item, amount)  # not implemented yet
            except:
                print 'failed_location'
