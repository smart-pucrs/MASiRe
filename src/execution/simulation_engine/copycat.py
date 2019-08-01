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

        self.logs[self.config['map']['maps'][0]] = self.simulation.log()
        self.config['map']['maps'].pop(0)

        if not self.config['map']['maps']:
            return 0
        return 1

    def restart(self):
        """Restart the simulation and returns the copy of the response.

        :return tuple: First position holding the agents, second position the social assets and the third holding
        the current step."""

        response = self.simulation.restart(self.config)
        return copy.deepcopy(response)

    def connect_agent(self, token):
        """Connect the agent and returns the copy of the response.

        :param token: The identifier of the agent.
        :return bool: True if the agent was connected else False."""

        response = self.simulation.connect_agent(token)
        return copy.deepcopy(response)

    def connect_social_asset(self, token):
        """Connect the social asset and returns the copy of the response.

        :param token: The identifier of the social asset.
        :return bool: True if the social asset was connected else False."""

        response = self.simulation.connect_social_asset(token)
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
