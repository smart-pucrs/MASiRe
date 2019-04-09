from src.communication.events.emiters import emit_pre_step
from src.simulation.simulation import Simulation


class SimulationManager:

    def __init__(self, config):
        self.simulation = Simulation(config)
        self.simulation.start()

    def do_pre_step(self):
        pre_step_response = self.simulation.do_pre_step()
        for agent in self.simulation.world.agents:
            emit_pre_step(pre_step_response, agent.token)

    def do_step(self, actions_list):
        return self.simulation.do_step(actions_list)
