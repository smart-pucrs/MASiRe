from src.communication.events.emiters import response_to_action, emit_pre_step
from src.simulation.simulation import Simulation


class SimulationManager:

    def __init__(self, config):
        self.simulation = Simulation(config)
        self.agents, initial_percepts = self.simulation.start()

    def start_simulation(self):
        pass

    def do_step(self, actions_list):
        step_response = self.simulation.do_step(actions_list)
        return step_response

    def do_pre_step(self):
        pre_step_response = self.simulation.do_pre_step()
        return pre_step_response

    def agents_list(self):
        agents_str = []
        for agent in self.agents:
            agents_str.append(agent.__repr__())
        return agents_str
