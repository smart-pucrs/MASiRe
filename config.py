import json
from pprint import pprint

with open('config.json') as f:
    data = json.load(f)
#data["maps"][0]["id"] 


idMatch = data["map"]["id"]
steps = data["map"]["steps"]
mapMatch = data["map"]["map"]
minLon = data["map"]["minLon"]
maxLon = data["map"]["maxLon"]
minLat = data["map"]["minLat"]
maxLat = data["map"]["maxLat"]
centerLat = data["map"]["centerLat"]
centerLon = data["map"]["centerLon"]
proximity = data["map"]["proximity"]
randomSeed = data["map"]["randomSeed"]
goToCost = data["map"]["gotoCost"]
rechargeRate = data["map"]["rechargeRate"]

numCar = data["agents"]["car"]
numDrone = data["agents"]["drone"]
numBoat = data["agents"]["boat"]

speedDrone = data["roles"]["drone"]["speed"]
capPhysicalDrone = data["roles"]["drone"]["capacity_physical"]
capVirtualDrone = data["roles"]["drone"]["capacity_virtual"]
batteryDrone = data["roles"]["drone"]["battery"]
photoAbDrone = data["roles"]["drone"]["abilities"][0]
victimAbDrone = data["roles"]["drone"]["abilities"][1]
waterAbDrone = data["roles"]["drone"]["abilities"][2]
percieveDrone = data["roles"]["drone"]["percieve"]
kindDrone = data["roles"]["drone"]["kind"]


speedCar = data["roles"]["car"]["speed"]
capPhysicalCar = data["roles"]["car"]["capacity_physical"]
capVirtualCar = data["roles"]["car"]["capacity_virtual"]
batteryCar = data["roles"]["car"]["battery"]
photoAbCar = data["roles"]["car"]["abilities"][0]
victimAbCar = data["roles"]["car"]["abilities"][1]
waterAbCar = data["roles"]["car"]["abilities"][2]
percieveCar = data["roles"]["car"]["percieve"]
kindCar = data["roles"]["car"]["kind"]


speedBoat = data["roles"]["boat"]["speed"]
capPhysicalBoat = data["roles"]["boat"]["capacity_physical"]
capVirtualBoat = data["roles"]["boat"]["capacity_virtual"]
batteryBoat = data["roles"]["boat"]["battery"]
photoAbBoat = data["roles"]["boat"]["abilities"][0]
victimAbBoat = data["roles"]["boat"]["abilities"][1]
waterAbBoat = data["roles"]["boat"]["abilities"][2]
percieveBoat = data["roles"]["boat"]["percieve"]
kindBoat = data["roles"]["boat"]["kind"]






print(percieveBoat)