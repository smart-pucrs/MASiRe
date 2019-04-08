from src.manager.simulation_manager import SimulationManager
import json


class SimulationSingleton:
    __shared_state = {}

    def __init__(self, path=''):
        if path:
            self.__shared_state['simulation_manager'] = self.get_instance(path)
        self.__dict__ = self.__shared_state

    def get_instance(self, path):
        with open(path, 'r') as simulation_config:
            json_config = json.loads(simulation_config.read())
            simulation_manager = SimulationManager(json_config)
            return simulation_manager

