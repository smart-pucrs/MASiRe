import json

with open('config.json') as f:
    data = json.load(f)

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


quadSize = data["generate"]["quadSize"]
floodProbability = data["generate"]["floodProbability"]

floodMinPeriod = data["generate"]["flood"]["minPeriod"]
floodMaxPeriod = data["generate"]["flood"]["maxPeriod"]

circleMinRad = data["generate"]["flood"]["circle"]["minRadius"]
circleMaxRad = data["generate"]["flood"]["circle"]["maxRadius"]

rectMinHeight = data["generate"]["flood"]["rectangle"]["minHeight"]
rectMaxHeight = data["generate"]["flood"]["rectangle"]["minHeight"]
rectMinLength = data["generate"]["flood"]["rectangle"]["minLength"]
rectMaxLength = data["generate"]["flood"]["rectangle"]["maxLength"]

photoSize = data["generate"]["photo"]["size"]
photoMinAmount = data["generate"]["photo"]["minAmount"]
photoMaxAmount = data["generate"]["photo"]["maxAmount"]
photoVictimProb = data["generate"]["photo"]["victimProbability"]

victimMinSize = data["generate"]["victim"]["minSize"]
victimMaxSize = data["generate"]["victim"]["maxSize"]
victimMinAmount = data["generate"]["victim"]["minAmount"]
victimMaxAmount = data["generate"]["victim"]["maxAmount"]
victimMinLifetime = data["generate"]["victim"]["minLifetime"]
victimMaxLifetime = data["generate"]["victim"]["maxLifetime"]

waterSampleSize = data["generate"]["waterSample"]["size"]
waterSampleMin = data["generate"]["waterSample"]["minAmount"]
WaterSampleMax = data["generate"]["waterSample"]["maxAmount"]

print(victimMinLifetime)