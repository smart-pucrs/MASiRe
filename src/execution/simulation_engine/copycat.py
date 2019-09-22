import copy
import datetime
from simulation_engine.simulation import Simulation


class CopyCat:
    """Class that copy all the objects and responses from inside the engine to prevent from being changed."""

    def __init__(self, config):
        self.config = config
        self.logs = {}
        self.simulation = Simulation(config)

    def log(self):
        """Save the log from the simulation and remove the first map from the maps list on the configuration file.

        The first map is removed from the list so when the simulation restart it will use the new map.

        :return int: 1 if can be restarted else 0."""

        self.logs[self.config['map']['maps'][0]['osm']] = self.simulation.log()
        self.config['map']['maps'].pop(0)
        print('MAP: ', self.config['map']['maps'])
        if not self.config['map']['maps']:
            return 0

        return 1

    def restart(self):
        """Restart the simulation, returns the copy of the response and the report of the agents.

        :return tuple, dict: First position holding the agents, second position the social assets, the third holding
        the current step and a dictionary with the report of the agents."""

        response = self.simulation.restart(self.config)
        return copy.deepcopy(response)

    def connect_agent(self, token):
        """Connect the agent and returns the copy of the response.

        :param token: The identifier of the agent.
        :return bool: True if the agent was connected else False."""

        response = {'agent_percepts': self.simulation.connect_agent(token),
                    'map_percepts': self.simulation.get_map_percepts()}

        return copy.deepcopy(response)

    def connect_social_asset(self, main_token, token):
        """Connect the social asset and returns the copy of the response.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was connected else False."""

        response = {'agent_percepts': self.simulation.connect_social_asset(main_token, token),
                    'map_percepts': self.simulation.get_map_percepts()}

        return copy.deepcopy(response)

    def finish_social_asset_connections(self, tokens):
        response = self.simulation.get_social_assets_by_tokens(tokens)

        return copy.deepcopy(response)

    def disconnect_agent(self, token):
        """Disconnect the agent and returns the copy of the response.

        :param token: The identifier of the agent.
        :return bool: True if the agent was connected else False."""

        response = self.simulation.disconnect_agent(token)
        return copy.deepcopy(response)

    def disconnect_social_asset(self, token):
        """Disconnect the social asset and returns the copy of the response.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was connected else False."""

        response = self.simulation.disconnect_social_asset(token)
        return copy.deepcopy(response)

    def start(self):
        """Start the simulation and return the copy of the response.

        :return tuple: First position holding the agents, second position the social assets and the third holding
        the current step."""

        response = self.simulation.start()
        return copy.deepcopy(response)

    def do_step(self, token_action_list):
        """Do one step and return the copy of the response

        :param token_action_list: The actions sent by each agent or social asset.
        :return tuple|None: If not terminated the first position holds the results from the actions sent and the second,
        the current step, else None."""

        response = self.simulation.do_step(token_action_list)
        return copy.deepcopy(response)

    def get_logs(self):
        """Return a copy of all the logs along with the folder structure based on date.

        :return list: List containing the folder structure and the logs."""

        return [
            datetime.datetime.now().year,
            datetime.datetime.now().strftime('%B'),
            datetime.datetime.now().strftime('%A'),
            datetime.datetime.now().hour,
            datetime.datetime.now().minute,
            copy.deepcopy(self.config['map']['id']),
            copy.deepcopy(self.logs)
        ]

    def match_report(self):
        return self.simulation.match_report()

    def simulation_report(self):
        return self.simulation.simulation_report()
