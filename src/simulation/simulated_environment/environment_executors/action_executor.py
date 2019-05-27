# based https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from simulation.exceptions.exceptions import *


class ActionExecutor:

    def __init__(self, config, world, logger):
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
        self.route = world.generator.router
        self.logger = logger

    def execute_actions(self, actions, cdm_location, step):
        """
        [Method that parses all the actions recovered from the communication core
        and calls its execution during a step.]

        :param step: current step of simulation
        :param cdm_location: Location of the cdm specified in the config file
        :param actions: A json file sent by the communication core
        containing all the actions, including the necessary parameters,
        and its respective agents.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """

        action_results = []

        for obj in actions:
            token = obj['token']
            action = (obj['action'], *obj['parameters'])
            result = self.execute(self.world.agents[token], action, cdm_location, step)

            agent_copy = self.world.agents[obj['token']].json()
            parameters = action[1] if len(action) == 2 else []
            self.logger.register_agent_action(
                token=agent_copy['token'],
                role=agent_copy['role'],
                result=True if result is None else result,
                name=agent_copy['agent_info']['name'],
                action=action[0],
                parameters=parameters
            )
            del agent_copy['agent_info']
            action_results.append((obj['token'], agent_copy, result))

        return action_results

    def execute(self, agent, action, cdm_location, step):
        """
        [Method that tries to execute a single action for a parametrized agent.
        The action may contain necessary parameters.
        This method is also responsible for calling the manager of the parametrized
        agent, so than it can modify its private attributes.]

        :param cdm_location: Location of the cdm specified in the config file
        :param agent: Agent responsible for calling a specific command (per step).
        :param action: The agent's desired action to be executed, including its
        necessary parameters.
        :return: A list containing every agent's action result,
        marking it with a success or failure flag.
        """

        action_name = action[0]
        parameters = action[1:]

        agent.last_action = action_name
        agent.last_action_result = False

        if action_name is None:
            return 'No action given.'

        elif action_name == 'pass':
            agent.last_action_result = True
            return
        try:
            if action_name == 'move':
                if len(parameters) == 1:
                    if parameters[0] == 'cdm':
                        location = cdm_location
                    else:
                        raise Failed_unknown_facility('Unknown facility')
                else:
                    raise Failed_wrong_param('More than 1 or less than than 1 parameters were given')

                if self.get_location(agent.location, location):
                    agent.route, distance = [], 0
                    return

                if not agent.check_battery():
                    raise Failed_insufficient_battery('Not enough battery to complete this step.')

                list_of_nodes = []
                for event in self.world.events[:step]:
                    if event['flood'] and event['flood'].active:
                        list_of_nodes.extend(event['flood'].list_of_nodes)

                if not agent.route:
                    self.get_route(agent, location, list_of_nodes)
                elif agent.route[-1] != location:
                    self.get_route(agent, location, list_of_nodes)

                if not agent.destination_distance:
                    return

                agent.last_action_result = True
                agent.discharge()
                agent.location = agent.route.pop(0)

            elif action_name == 'deliver_physical':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                # ================= TEST CODE HERE ==================
                #agent.location = cdm_location

                if self.get_location(agent.location, cdm_location):
                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0], amount=parameters[1])

                    agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'deliver_virtual':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                # ================= TEST CODE HERE ==================
                #agent.location = cdm_location

                if self.get_location(agent.location, cdm_location):
                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0], amount=parameters[1])

                    agent.last_action_result = True
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'charge':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                # ================= TEST CODE HERE ==================
                #agent.location = cdm_location

                if self.get_location(agent.location, cdm_location):
                    agent.charge()
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'rescue_victim':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for event in self.world.events:
                    for victim in event['victims']:

                        # ================= TEST CODE HERE ==================
                        #agent.location = victim.location

                        if victim.active and self.get_location(victim.location, agent.location):
                            agent.add_physical_item(victim)
                            victim.active = False
                            agent.last_action_result = True
                            return

                raise Failed_unknown_item('No victim by the given location is known.')

            elif action_name == 'collect_water':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for event in self.world.events:
                    for water_sample in event['water_samples']:
                        # ================= TEST CODE HERE ==================
                        #agent.location = water_sample.location

                        if water_sample.active and self.get_location(water_sample.location, agent.location):
                            agent.add_physical_item(water_sample)
                            water_sample.active = False
                            agent.last_action_result = True
                            return

                raise Failed_location('The agent is not in a location with a water sample.')

            elif action_name == 'photograph':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for event in self.world.events:
                    for photo in event['photos']:

                        # ================= TEST CODE HERE ==================
                        #agent.location = photo.location

                        if photo.active and self.get_location(photo.location, agent.location):
                            agent.add_virtual_item(photo)
                            photo.active = False
                            agent.last_action_result = True
                            return

                raise Failed_location('The agent is not in a location with a photograph event.')

            elif action_name == 'search_social_asset':
                if len(parameters) != 1:
                    raise Failed_wrong_param('Wrong amount of parameters given.')

                for social_asset in self.world.social_assets:
                    if social_asset in agent.social_assets:
                        continue

                    if social_asset.active and social_asset.profession == parameters[0]:
                        agent.social_assets.append(social_asset)
                        agent.last_action_result = True
                        return

                raise Failed_no_social_asset('No social asset found for the needed purposes.')

            elif action_name == 'get_social_asset':
                if parameters:
                    raise Failed_wrong_param('Wrong amount of parameters given.')

                if agent.role == 'drone':
                    raise Failed_invalid_kind('Agent role does not support carrying social asset.')

                for social_asset in self.world.social_assets:
                    for social_asset_agent in agent.social_assets:
                        if social_asset_agent == social_asset:
                            if self.get_location(agent.location, social_asset.location) and social_asset.active:
                                agent.add_physical(social_asset)
                                agent.last_action_result = True
                                social_asset.active = False
                                return

                raise Failed_no_social_asset('Invalid social asset requested.')

            elif action_name == 'analyze_photo':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                if len(agent.virtual_storage_vector) == 0:
                    raise Failed_item_amount('The agent has no photos to analyze.')

                for photo in agent.virtual_storage_vector:
                    for victim in photo.victims:
                        victim.active = True

                # clears virtual storage
                agent.last_action_result = True
                agent.virtual_storage_vector = []
                agent.virtual_storage = agent.virtual_capacity

            else:
                return 'Wrong action name'

        except Failed_no_social_asset as e:
            return e.message

        except Failed_wrong_param as e:
            return e.message

        except Failed_no_route as e:
            return e.message

        except Failed_insufficient_battery as e:
            return e.message

        except Failed_capacity as e:
            return e.message

        except Failed_invalid_kind as e:
            return e.message

        except Failed_item_amount as e:
            return e.message

        except Failed_location as e:
            return e.message

        except Failed_unknown_facility as e:
            return e.message

        except Failed_unknown_item as e:
            return e.message

    def agent_delivery(self, agent, kind, item, amount=None):
        """
        [Method that ensures the correct delivery of the current agent's items
        to the CDM.]

        :param agent: The agent which will have its items removed.
        :param kind: The type of the items to be removed (tagged by physical or virtual).
        :param item: The item to be removed.
        :param amount: The amount of items that shares the same characteristics of the
        parametrized item to be removed.
        """

        removed_items = []

        if amount is None:
            if kind == 'physical':
                removed_items = agent.remove_physical_item(item)

            elif kind == 'virtual':
                removed_items = agent.remove_virtual_item(item)

            else:
                raise Failed_invalid_kind('Invalid item to deliver')

        else:

            if amount < 1:
                raise Failed_item_amount('The given amount is less than 1')

            if kind == 'physical':
                if amount > len(agent.physical_storage_vector):
                    raise Failed_item_amount('The given amount is greater than what the agent is carrying')

                removed_items = agent.remove_physical_item(item, amount)

            elif kind == 'virtual':
                if amount > len(agent.virtual_storage_vector):
                    raise Failed_item_amount('The given amount is greater than what the agent is carrying')

                removed_items = agent.remove_virtual_item(item, amount)

        if len(removed_items) == 0:
            raise Failed_unknown_item('No item by the given name is known.')

        if kind == 'physical':
            self.world.cdm.add_physical_items(removed_items, agent.token)

        else:
            self.world.cdm.add_virtual_items(removed_items, agent.token)

    def get_route(self, agent, location, list_of_nodes):
        if agent.role == 'drone' or agent.role == 'boat':
            agent.route, distance = self.route.get_route(agent.location, location, agent.role, int(agent.speed) / 2,
                                                         list_of_nodes)
            agent.destination_distance = distance
        else:
            start_node = self.route.get_closest_node(*agent.location)
            end_node = self.route.get_closest_node(*location)
            route_result, route = self.route.get_route(start_node, end_node, False, 4, list_of_nodes)

            if route_result == 'success':
                agent.route = route
            else:
                raise Failed_no_route()

            agent.destination_distance = self.route.node_distance(start_node, end_node)

        print("ROUTE ->>> ", agent.route)

    def get_location(self, x, y):
        proximity = self.config['map']['proximity']

        if x[0] < y[0]:
            if x[0] + proximity >= y[0]:
                lat = True
            else:
                lat = False
        else:
            if x[0] - proximity <= y[0]:
                lat = True
            else:
                lat = False

        if x[1] < y[1]:
            if x[1] + proximity >= y[1]:
                lon = True
            else:
                lon = False
        else:
            if x[1] - proximity <= y[1]:
                lon = True
            else:
                lon = False

        return lat and lon
