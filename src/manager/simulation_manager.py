from src.communication.events.emiters import emit_pre_step
from src.simulation.simulation import Simulation


class SimulationManager:

    def __init__(self, config):
        self.simulation = Simulation(config)

    def start_simulation(self):
        self.agents, initial_percepts = self.simulation.start()

    def do_step(self, actions_list):
        return self.simulation.do_step(actions_list)

    def do_pre_step(self):
        pre_step_response = self.simulation.do_pre_step()
        for agent in self.agents:
            emit_pre_step(pre_step_response, agent.token)
