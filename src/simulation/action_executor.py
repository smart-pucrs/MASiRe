# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from src.simulation.exceptions import *
from src.simulation.data.events.water_sample import WaterSample
from src.simulation.data.events.photo import Photo

class ActionExecutor:

    def __init__(self, config):
        self.config = config
        self.world = None

    def execute_actions(self, world, actions):

        action_results = [None for x in range(len(actions))]

        for idx, command in enumerate(actions):
            agent = world.agents[command[0]]
            action = command[1]

        self.world = world
        self.execute(agent, action)
        action_results[idx] = agent.last_action_result

        return action_results

        # PARAMETER = AGENT['PARAMETERS']

        action_name = action[0]
        action_parameters = action[1:]

    def execute(self, agent, command, world):

        # action = ('move', '34', '32')
        print(agent)
        print(command)

        action = command[0]
        parameters = command[1:]

        if action is None:

            agent.last_action = None
            agent.last_action_result = False

            print('Error: failed_no_action')

        elif action is 'move':

            agent.last_action = 'move'

            try:

                if parameters.size() < 1 or parameters.size() > 2:
                    raise Failed_wrong_param ('Less than 1 or more than 2 parameters were given.')

                if len(parameters) == 1:

                    facility = world.facilities[parameters[0]]

                    if agent.location is facility.location:

                        if agent.route is None:
                            route = self._map.create_route_facility(agent.role.location, facility) #not implemented yet
                            agent.route = route
                            agent.last_action_result = True

                        else:
                            agent.location = agent.route.next_node() #not implemented yet
                            agent.last_action_result = True

                elif len(parameters) == 2:

                    latitude = parameters[0]
                    longitude = parameters[1]

                    agent.location = [latitude, longitude]
                    agent.last_action_result = True

            except Failed_wrong_param as e:
                agent.last_action_result = False
                print(e.message)

            except Failed_unknown_facility:
                agent.last_action_result = False

            except Failed_no_route:
                agent.last_action_result = False

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'deliver_physical':

            agent.last_action = 'deliver_physical'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location is world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('physical', parameters[0])
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver('physical', parameters[0], parameters[1])
                        agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param:
                agent.last_action_result = False

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except Failed_unknown_item:
                agent.last_action_result = False
                print('Error: Failed_unknown_item')

            except Failed_item_amount:
                agent.last_action_result = False
                print('Error: failed_item_amount')

            except:
                agent.last_action_result = False
                print('Error: failed')


        elif action is 'deliver_virtual':

            agent.last_action = 'deliver_virtual'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location is world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('virtual', parameters[0])
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver('virtual', parameters[0], parameters[1])
                        agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except Failed_unknown_item:
                agent.last_action_result = False
                print('Error: Failed_unknown_item')

            except Failed_item_amount:
                agent.last_action_result = False
                print('Error: failed_item_amount')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'charge':

            agent.last_action = 'charge'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                if agent.location is world.cdm.location:
                    agent.charge()
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'rescue_victim':

            agent.last_action = 'rescue_victim'

            try:

                if len(parameters) > 1:
                    raise Failed_wrong_param('More or less than 1 parameter was given.')

                victim = world.victims[parameters[0]]

                if victim is None:
                    raise Failed_unknown_item('No victim by the given ID is known.')

                if victim.location is agent.location:
                    world.remove_victim(victim) #not implemented yet
                    weight = victim.get_weight() #not implemented yet
                    agent.add_physical_item(victim.id, weight)
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not at the same location as the victim.')

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except Failed_unknown_item:
                agent.last_action_result = False
                print('Error: Failed_unknown_item')

            except Failed_capacity:
                agent.last_action_result = False
                print('Error: failed_capacity')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'collect_water':

            agent.last_action = 'collect_water'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                facility = world.facilities[agent.location]

                if agent.location is world.facility.location:

                        water = WaterSample()
                        agent.add_physical_item(water)
                        agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not in a location with a water sample.')

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except Failed_capacity:
                agent.last_action_result = False
                print('Error: failed_capacity')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'photograph':

            agent.last_action = 'photograph'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                facility = world.facilities[agent.location]

                if facility.location is agent.location:

                    if facility.id is 'photo':
                        photo = Photo()
                        agent.add_virtual_item(photo)
                        agent.last_action_result = True

                    else:
                        raise Failed_invalid_kind('Invalid item to photograph.')

                else:
                    raise Failed_location('The agent is not in a location with a photography event.')

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except Failed_location:
                agent.last_action_result = False
                print('Error: failed_location')

            except Failed_capacity:
                agent.last_action_result = False
                print('Error: failed_capacity')

            except Failed_invalid_kind:
                agent.last_action_result = False
                print('Error: failed_invalid_kind')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'search_social_asset':

            agent.last_action = 'search_social_asset'

            try:

                if len(parameters) != 1 or len(parameters) != 3:
                    raise Failed_wrong_param('More than 3, 2, or 0 parameters were given.')

                if len(parameters) == 1:
                    assets = world.map.search_social_asset(radius, agent.location) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

                else:
                    assets = world.map.search_social_asset(radius, latitude, longitude) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action is 'analyze_photo':
            agent.last_action = 'analyze_photo'

            try:
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                agent.remove_virtual_item('photo')
                agent.last_action_result = True

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except Failed_item_amount:
                agent.last_action_result = False
                print('Error: failed_item_amount')

            except :
                agent.last_action_result = False
                print('Error: failed')


        else:
            agent.last_action_result = False
            print('Error: failed')

    def agent_deliver(self, agent, kind, amount = None):

        total_removed = 0

        if amount is None:
            if kind is 'physical':
                total_removed = agent.remove_physical_item('physical')

            elif kind is 'virtual':
                total_removed = agent.remove_virtual_item('virtual')

            else:
                raise Failed_invalid_kind('Invalid item to deliver')

            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located in the CDM.')

        elif amount is not None:
            if not verify(amount): #not implemented yet (boolean)
                raise Failed_item_amount('The given amount is not an integer, less than 1 or greater than what the agent is carrying.')

            if kind is 'physical':
                total_removed = agent.remove_physical_item('physical', amount)

            elif kind is 'virtual':
                total_removed = agent.remove_virtual_item('virtual', amount)

            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located at the CDM.')

