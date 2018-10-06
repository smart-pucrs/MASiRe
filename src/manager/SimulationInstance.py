from src.manager.SimulationManager import SimulationManager
import json

simulation_manager = None


def get_instance(path):
    global simulation_manager
    if simulation_manager is None:
        f = open(path, 'r').read()
        config = json.loads(f)
        simulation_manager = SimulationManager(config)
    return simulation_manager
