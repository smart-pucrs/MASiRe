import json

from src.simulation.data.role import Role
from src.simulation.world import World
from src.simulation.data.agent import Agent
from src.simulation.simulation import Simulation

config = json.loads('{"map":{"id":"2018-SampleSimulation","steps":10,"map":"PortoAlegre","minLon":2.26,"maxLon":2.41,"minLat":48.82,"maxLat":48.9,"centerLat":48.8424,"centerLon":2.3209,"proximity":5,"randomSeed":2018,"gotoCost":2,"rechargeRate":2},"agents":{"car":2,"drone":4,"boat":1},"roles":{"drone":{"speed":7,"capacity_physical":10,"capacity_virtual":10,"battery":20,"abilities":[["photo",7.2,2.3],["victim",0],["water",0]],"percieve":5,"kind":"air"},"car":{"speed":7,"capacity_physical":10,"capacity_virtual":10,"battery":20,"abilities":[["photo",7.2,2.3],["victim",5],["water",0]],"percieve":5,"kind":"earth"},"boat":{"speed":7,"capacity_physical":10,"capacity_virtual":10,"battery":20,"abilities":[["photo",7.2,2.3],["victim",5],["water",10]],"percieve":5,"kind":"water"}},"generate":{"quadSize":2,"floodProbability":5,"flood":{"minPeriod":40,"maxPeriod":80,"circle":{"minRadius":34,"maxRadius":90},"rectangle":{"minHeight":30,"maxHeight":70,"minLength":20,"maxLength":60}},"photo":{"size":3,"minAmount":5,"maxAmount":10,"victimProbability":60},"victim":{"minSize":5,"maxSize":10,"minAmount":5,"maxAmount":10,"minLifetime":30,"maxLifetime":40},"waterSample":{"size":4,"minAmount":5,"maxAmount":10}}}')

simulation = Simulation(config)

print(simulation.start())

simulation.do_step([('1', ('move', '34', '32')), ('2', ('photograph')),('2',('analyze_photo')), ('2',('rescue_victim','victim'))])


print(simulation.world.events)


