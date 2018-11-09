# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from src.simulation.exceptions import *


class ActionExecutor:

    def __init__(self, config, world):
        """
        [Constructor of the agent executor, which is responsible for
        executing every agent's desired action.]

        :param config: The configuration file which contains all the
        necessary information for the simulation.
        :param world: The world class, which is responsible for manipulating
        the simulation universe, including all the events and facilities.
        """

        self.config = config
        self.world = world

    def execute_actions(self, actions):
        """
        [Method that parses all the actions recovered from the communication core
        and calls its execution during a step.]
        
        :param actions: A json file sent by the communication core
        containing all the actions, including the necessary parameters,
        and its respective agents.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """

        action_results = [None for x in range(len(actions))]

        for idx, command in enumerate(actions):
            agent = self.world.agents[int(command[0])]
            action = command[1]

            self.execute(agent, action)
            action_results[idx] = agent.last_action_result

        return action_results

    def execute(self, agent, command):
        """
        [Method that tries to execute a single action for a parametrized agent.
        The action may contain necessary parameters.
        This method is also responsible for calling the manager of the parametrized
        agent, so than it can modify its private attributes.]

        :param agent: Agent responsible for calling a specific command (per step).
        :param command: The agent's desired action to be executed, including its
        necessary parameters.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """

        #print(agent)
        #print(command)

        if not isinstance(command, str):
            action = command[0]
            parameters = command[1:]

        else:
            action = command
            parameters = []

        agent.last_action = action
        agent.last_action_result = False

        if action == None:
            print('Error: failed_no_action')

        elif action == 'move':
            try:
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if len(parameters) == 1:
                    if parameters[0] != 'cdm':
                        raise Failed_wrong_param('Unknown facility')
                    
                    location = self.world.cdm.location

                else:
                    location = [parameters[0], parameters[1]]

                if agent.location == location:
                    # already arrived. raise error?
                    pass

                if agent.route == None:
                    agent.route = self.world.create_route_coordinate(agent.location, self.world.cdm.location)

                    if agent.route == None: 
                        raise Failed_no_route()

                agent.last_action_result = True
                agent.location = agent.route.next_node()

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

                if agent.location == self.world.cdm.location:
                    if len(parameters) == 1:
                        agent.last_action_result = True
                        self.agent_deliver(agent, 'physical', parameters[0])

                    elif len(parameters) == 2:
                        agent.last_action_result = True
                        self.agent_deliver(agent, 'physical', parameters[0], parameters[1])
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_invalid_kind as e:
                print('Error: failed_invalid_kind')
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

                if agent.location == self.world.cdm.location:
                    if len(parameters) == 1:
                        self.agent_deliver(agent, 'virtual', parameters[0])
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver(agent, 'virtual', parameters[0], parameters[1])
                        agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_invalid_kind as e:
                print('Error: failed_invalid_kind')
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

                if agent.location == self.world.cdm.location:
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
                if len(parameters) != 1:
                    raise Failed_wrong_param('More or less than 1 parameter was given.')

                for flood in self.world.active_events:
                    for photo in flood.photos:
                        if photo.active and photo.location == agent.location:
                            flood.water_samples.remove(photo.id)
                            agent.add_physical_item(photo, 1)
                            photo.active = False
                            agent.last_action_result = True
                            return

                raise Failed_unknown_item('No victim by the given ID is known.')

            except Failed_wrong_param as e:
                print('Error: failed_wrong_param')
                print(e.message)

            except Failed_unknown_item as e:
                print('Error: failed_unknown_item')
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

                for water_sample in self.world.water_samples:
                    if water_sample.active and water_sample.location == agent.location:
                        water_sample.water_samples.remove(water_sample.id)
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

                for flood in self.world.active_events:
                    for photo in flood.photos:
                        if photo.active and photo.location == agent.location:
                            flood.photos.remove(photo.id)
                            agent.add_virtual_item(photo,1)
                            agent.last_action_result = True
                            return

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
                    #assets = self.world.search_social_asset(radius, agent.location) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

                else:
                    #assets = self.world.map.search_social_asset(radius, latitude, longitude) #not implemented yet
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

                for e in agent.virtual_storage_vector:
                    if e.id == 'photo':
                        agent.victims_to_rescue = e.victims
                        agent.remove_virtual_item(e)
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

        return agent.last_action_result


    #Method that ensures the correct removal of the current agent's items
    def agent_deliver(self, agent, kind, item, amount=None):
        """
        [Method that ensures the correct delivery of the current agent's items
        to the CDM.]

        :param agent:
        :param kind:
        :param item:
        :param amount:
        :return:
        """

        total_removed = 0

        if amount == None:

            if kind == 'physical':
                total_removed = agent.remove_physical_item(item)

            elif kind == 'virtual':
                total_removed = agent.remove_virtual_item(item)

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
                    raise Failed_item_amount('The given amount is not an integer, less than 1 or greater '
                                             'than what the agent is carrying.')

                total_removed = agent.remove_physical_item(item)

            elif kind == 'virtual':

                if amount < 1 or amount > agent.virtual_storage:
                    raise Failed_item_amount('The given amount is not an integer, less than 1 or greater '
                                             'than what the agent is carrying.')

                total_removed = agent.remove_virtual_item(item)


            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = self.world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located at the CDM.')