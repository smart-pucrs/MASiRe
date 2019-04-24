# based https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from simulation.exceptions.exceptions import *


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
        self.route = world.generator.router

    def execute_actions(self, actions, cdm_location):
        """
        [Method that parses all the actions recovered from the communication core
        and calls its execution during a step.]

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
            result = self.execute(self.world.agents[token], action, cdm_location)

            if result:
                print(result)

            action_results.append((obj['token'], self.world.agents[obj['token']].__dict__))

        return action_results

    def execute(self, agent, action, cdm_location):
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
            return 'No action given'

        elif action_name == 'pass':
            agent.last_action_result = True
            return
        try:
            if action_name == 'move':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if len(parameters) == 1:
                    if parameters[0] != 'cdm':
                        raise Failed_wrong_param('Unknown facility')

                    location = cdm_location

                else:
                    location = [parameters[0], parameters[1]]

                if agent.location == location:
                    agent.route, distance = [agent.location], 0
                    return

                if not agent.check_battery():
                    raise Failed_insufficient_battery('Not enough battery to complete this step')

                if not agent.route:
                    if agent.role == 'drone':
                        agent.route, distance = self.route.get_route(agent.location, location, True, int(agent.speed)/2)
                        agent.destination_distance = distance

                    else:
                        start_node = self.route.get_closest_node(*agent.location)
                        end_node = self.route.get_closest_node(*location)
                        route_result, route = self.route.get_route(start_node, end_node, False)

                        if route_result == 'success':
                            agent.route = route
                        else:
                            raise Failed_no_route()

                        agent.destination_distance = self.route.node_distance(start_node, end_node)

                agent.last_action_result = True
                agent.discharge()
                agent.location = agent.route.pop(0)

            elif action_name == 'deliver_physical':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location == cdm_location:
                    agent.last_action_result = True

                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0], amount=parameters[1])
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'deliver_virtual':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location == cdm_location:
                    agent.last_action_result = True

                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0], amount=parameters[1])
                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'charge':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                if agent.location == cdm_location:
                    agent.charge()
                    agent.last_action_result = True

                else:
                    raise Failed_location('The agent is not located at the CDM.')

            elif action_name == 'rescue_victim':
                if len(parameters) != 1:
                    raise Failed_wrong_param('More or less than 1 parameter was given.')

                for victim in self.world.victims:
                    victim_location = self.route.get_node_coord(victim.node)
                    if victim.active and parameters[0] == victim.id and victim_location == agent.location:
                        agent.add_physical_item(victim)
                        victim.active = False
                        victim.in_photo = False
                        agent.last_action_result = True
                        return

                raise Failed_unknown_item('No victim by the given ID is known.')

            elif action_name == 'collect_water':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for water_sample in self.world.water_samples:
                    water_sample_location = self.route.get_node_coord(water_sample.node)
                    if water_sample.active and water_sample_location == agent.location:
                        agent.add_physical_item(water_sample)
                        water_sample.active = False
                        agent.last_action_result = True
                        return

                raise Failed_location('The agent is not in a location with a water sample.')

            elif action_name == 'photograph':
                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                for photo in self.world.photos:
                    photo_location = self.route.get_node_coord(photo.node)
                    if photo.active and photo_location == agent.location:
                        agent.add_virtual_item(photo)
                        photo.active = False
                        agent.last_action_result = True
                        return

                raise Failed_location('The agent is not in a location with a photograph event.')

            elif action_name == 'search_social_asset':
                if len(parameters) != 1:
                    raise Failed_wrong_param('Wrong amount of parameters given.')
                for social_asset in self.world.social_assets:
                    social_asset_location = self.route.get_node_coord(social_asset.node)

                    if social_asset.active and social_asset.profession == parameters[0]:
                        agent.add_physical_item(social_asset)
                        social_asset.active = False
                        agent.last_action_result = social_asset_location
                        agent.last_action = social_asset
                        break

                if not agent.last_action_result:
                    raise Failed_no_social_asset('No social asset found for the needed purposes')

            except Failed_wrong_param as e:
                return e.message

                raise Failed_no_social_asset('Invalid social asset requested.')

            # assumes the only virtual items in the simulation are photos
            elif action == 'analyze_photo':
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
            if amount < 1 or amount > agent.virtual_storage:
                raise Failed_item_amount('The given amount is not an integer, less than 1 or greater '
                                         'than what the agent is capable of carrying.')
            if kind == 'physical':
                removed_items = agent.remove_physical_item(item, amount)

            elif kind == 'virtual':
                removed_items = agent.remove_virtual_item(item, amount)

        if len(removed_items) == 0:
            raise Failed_unknown_item('No item by the given name is known.')

        if kind == 'physical':
            self.world.cdm.add_physical_items(removed_items, agent.agent_token)

        else:
            self.world.cdm.add_virtual_items(removed_items, agent.agent_token)
