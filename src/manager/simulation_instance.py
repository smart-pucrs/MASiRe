from src.manager.simulation_manager import SimulationManager
import json

simulation_manager = None


def get_instance():
    global simulation_manager
    if simulation_manager is None:
        print('Simulations has not been started')
        return None
    return simulation_manager


def start_manager(path):
    global simulation_manager
    f = open(path, 'r').read()
    config = json.loads(f)
    simulation_manager = SimulationManager(config)
