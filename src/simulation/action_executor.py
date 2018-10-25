# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/ActionExecutor.java
from src.simulation.exceptions import *
from src.simulation.data.events.water_sample import WaterSample
from src.simulation.data.events.photo import Photo

#Class responsible for executing every agents desired action
class ActionExecutor:

    def __init__(self, config, World):
        self.config = config
        self.world = World

    #Method that parses all the actions recovered from the communication core
    #Those actions represents the 'desire' of each agent
    def execute_actions(self, actions):

        action_results = [None for x in range(len(actions))]

        for idx, command in enumerate(actions):
            agent = self.world.agents[int(command[0])]
            action = command[1]

            self.execute(agent, action)
            # REMOVE THIS RETURN STATEMENT TO PROPERLY RUN THE SIMULATION
            return True
            action_results[idx] = agent.last_action_result

        return action_results

        # PARAMETER = AGENT['PARAMETERS']

        action_name = action[0]
        action_parameters = action[1:]


    #Method that tries to execute any possible action passed as a command line
    #Also responsible for managing the current agent's private attributes
    def execute(self, agent, command):

        # action = ('move', '34', '32')
        print(agent)
        print(command)

        action = command[0]
        parameters = command[1:]

        if action is None:

            agent.last_action = None
            agent.last_action_result = False

            print('Error: failed_no_action')

        elif action == 'move':
            # ===========REMOVER ESTE RETORNO PARA CONTINUAR A SIMULACAO==========
            return True

            agent.last_action = 'move'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if len(parameters) == 1:

                    facility = self.world.facilities[parameters[0]]

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

            except Failed_wrong_param as e: #pode ser tratado assim
                agent.last_action_result = False
                print(e.message)#print ou mensagem ao agente? comunicação?

            except Failed_unknown_facility:
                agent.last_action_result = False

            except Failed_no_route:
                agent.last_action_result = False

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action == 'deliver_physical':

            agent.last_action = 'deliver_physical'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location is self.world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('physical', parameters[0], self.world)
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

        elif action == 'deliver_virtual':

            agent.last_action = 'deliver_virtual'

            try:

                if len(parameters) < 1 or len(parameters) > 2:
                    raise Failed_wrong_param('Less than 1 or more than 2 parameters were given.')

                if agent.location is self.world.cdm.location:

                    if len(parameters) == 1:
                        self.agent_deliver('virtual', parameters[0], self.world)
                        agent.last_action_result = True

                    elif len(parameters) == 2:
                        self.agent_deliver('virtual', parameters[0], self.world, parameters[1])
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

        elif action == 'charge':

            agent.last_action = 'charge'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                if agent.location is self.world.cdm.location:
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

        elif action == 'rescue_victim':

            agent.last_action = 'rescue_victim'

            try:

                if len(parameters) > 1:
                    raise Failed_wrong_param('More or less than 1 parameter was given.')

                victim = self.world.victims[parameters[0]]

                if victim is None:
                    raise Failed_unknown_item('No victim by the given ID is known.')

                if victim.location is agent.location:
                    self.world.remove_victim(victim) #not implemented yet
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

        elif action == 'collect_water':

            agent.last_action = 'collect_water'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                facility = self.world.facilities[agent.location]

                if agent.location is facility.location:

                        water = WaterSample()
                        agent.add_physical_item(water)#(water, water.size)
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

        elif action == 'photograph':

            agent.last_action = 'photograph'

            try:

                if len(parameters) > 0:
                    raise Failed_wrong_param('Parameters were given.')

                facility = self.world.facilities[agent.location]

                if facility.location is agent.location:

                    if facility.id is 'photo':
                        photo = Photo()
                        agent.add_virtual_item(photo)#(photo, photo.size)
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

        elif action == 'search_social_asset':

            agent.last_action = 'search_social_asset'

            try:

                if len(parameters) != 1 or len(parameters) != 3:
                    raise Failed_wrong_param('More than 3, 2, or 0 parameters were given.')

                if len(parameters) == 1:
                    #assets = self.world.map.search_social_asset(radius, agent.location) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

                else:
                    #assets = self.world.map.search_social_asset(radius, latitude, longitude) #not implemented yet
                    #show assets to agent
                    agent.last_action_result = True

            except Failed_wrong_param:
                agent.last_action_result = False
                print('Error: failed_wrong_param')

            except:
                agent.last_action_result = False
                print('Error: failed')

        elif action == 'analyze_photo':
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


    #Method that ensures the correct removal of the current agent's items
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

            delivered = self.world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located in the CDM.')

        elif amount is not None:
            if not self.verify(amount): #not implemented yet (boolean)
                raise Failed_item_amount('The given amount is not an integer, less than 1 or greater than what the agent is carrying.')

            if kind is 'physical':
                total_removed = agent.remove_physical_item('physical', amount)

            elif kind is 'virtual':
                total_removed = agent.remove_virtual_item('virtual', amount)

            if total_removed == 0:
                raise Failed_unknown_item('No item by the given name is known.')

            delivered = self.world.cdm.deliver(agent, kind, total_removed) #not implemented yet (boolean)
            if not delivered:
                raise Failed_location('The agent is not located at the CDM.')

    #Method that guarantees that the amount value is correct
    def verify(self, amount):
        #checker for the amount value
        pass
