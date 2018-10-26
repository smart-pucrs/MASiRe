# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from src.simulation.exceptions import *
from src.simulation.data.events.water_sample import WaterSample
from src.simulation.data.events.photo import Photo

#Class responsible for executing every agents desired action
class ActionExecutor:

    def __init__(self, config):
        self.config = config
        self.world = None

    #Method that parses all the actions recovered from the communication core
    #Those actions represent the 'desire' of each agent
    def execute_actions(self, world, actions):

        action_results = [None for x in range(len(actions))]

        for idx, command in enumerate(actions):
            agent = world.agents[int(command[0])]
            action = command[1]

        self.world = world
        self.execute(agent, action, world)
        action_results[idx] = agent.last_action_result

        return action_results

        # PARAMETER = AGENT['PARAMETERS']

    #Method that tries to execute any possible action passed as a command line
    #Also responsible for managing the current agent's private attributes
    def execute(self, agent, command, world):

        # action = ('move', '34', '32')
        print(agent)
        print(command)

        action = command[0]
        parameters = command[1:]

        agent.last_action = action
        agent.last_action_result = False

        if action == None:

            print('Error: failed_no_action')

        elif action == 'move':

            agent.last_action = 'move'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if len(parameters) == 1:

                    facility = world.facilities[parameters[0]]

                    if agent.location == facility.location:

                        if agent.route == None:
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
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_unknown_facility as e:
                print('Error: failed_unknown_facility')
                print(e.message)

            except Failed_no_route as e:
                print('Error: failed_no_route')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'deliver_physical':

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location == world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('physical', parameters[0], world)
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver('physical', parameters[0], world, parameters[1])
                        agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except Failed_unknown_item as e:
                print('Error: Failed_unknown_item')
                print(e.message)

            except Failed_item_amount as e:
                print('Error: failed_item_amount')
                print(e.message)

            except:
                print('Error: failed')


        elif action == 'deliver_virtual':

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location == world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('virtual', parameters[0], world)
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver('virtual', parameters[0], world, parameters[1])
                        agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except Failed_unknown_item as e:
                print('Error: Failed_unknown_item')
                print(e.message)

            except Failed_item_amount as e:
                print('Error: failed_item_amount')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'charge':

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                if agent.location == world.cdm.location:
                    agent.charge()
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'rescue_victim':

            try:

                if len(parameters) > 1:
                    raise Failed_wrong_param('More or less than 1 parameter was given.')

                victim = world.victims[parameters[0]]

                if victim == None:
                    raise Failed_unknown_item('No victim by the given ID is known.')

                if victim.location == agent.location:
                    world.remove_victim(victim) #not implemented yet
                    weight = victim.get_weight() #not implemented yet
                    agent.add_physical_item(victim.id, weight)
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not at the same location as the victim.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except Failed_unknown_item as e:
                print('Error: Failed_unknown_item')
                print(e.message)

            except Failed_capacity as e:
                print('Error: failed_capacity')
                print(e.message)

            except:
                print('Error: failed')


        elif action == 'collect_water':

            try:
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for flood in world.active_events:
                    for water_sample in flood.water_samples:
                        if water_sample.active and water_sample.location == agent.location:
                            agent.add_physical_item(water_sample, 1)
                            water_sample.active = False
                            agent.last_action_result = True
                            return
                if not agent.last_action_result:
                    raise Failed_location('The agent is not in a location with a water sample.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except Failed_capacity as e:
                print('Error: failed_capacity')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'photograph':

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for flood in world.active_events:
                    for photo in flood.photo:
                        if photo.active and photo.location == agent.location:
                            agent.add_virtual_item(photo,1)
                            agent.last_action_result = True
                            return
                else:
                    raise Failed_location('The agent is not in a location with a photography event.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_location as e:
                print('Error: failed_location')
                print(e.message)

            except Failed_capacity as e:
                print('Error: failed_capacity')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'search_social_asset':

            try:

                if len(parameters) != 1 or len(parameters) != 3:
                    raise Failed_wrong_param('More than 3, 2, or 0 parameters were given.')

                if len(parameters) == 1:
                    #assets = world.map.search_social_asset(radius, agent.location) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

                else:
                    #assets = world.map.search_social_asset(radius, latitude, longitude) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except:
                print('Error: failed')

        elif action == 'analyze_photo':

            try:
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                agent.remove_virtual_item('photo')
                agent.last_action_result = True

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_item_amount as e:
                print('Error: failed_item_amount')
                print(e.message)

            except :
                print('Error: failed')


        else:
            print('Error: failed')


    #Method that ensures the correct removal of the current agent's items
    def agent_deliver(self, agent, kind, amount=None):

        total_removed = 0

        if amount == None:
            if kind == 'physical':
                total_removed = agent.remove_physical_item('physical')

            elif kind == 'virtual':
                total_removed = agent.remove_virtual_item('virtual')

            else:
                raise Failed_invalid_kind('Invalid item to deliver')

            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = self.world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located in the CDM.')

        elif amount != None:

            if kind == 'physical':
                if amount < 1 or amount > agent.physical_storage:
                    raise Failed_item_amount('The given amount is not an integer, less than 1 or greater than what the agent is carrying.')
                total_removed = agent.remove_physical_item('physical', amount)

            elif kind == 'virtual':
                if amount < 1 or amount > agent.virtual_storage:
                    raise Failed_item_amount('The given amount is not an integer, less than 1 or greater than what the agent is carrying.')
                total_removed = agent.remove_virtual_item('virtual', amount)

            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = self.world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located at the CDM.')
