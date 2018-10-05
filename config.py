import json
from pprint import pprint

with open('config.json') as f:
    data = json.load(f)

id_match = data["map"]["id"]
steps = data["map"]["steps"]
map_match = data["map"]["map"]
min_lon = data["map"]["minLon"]
max_lon = data["map"]["maxLon"]
min_lat = data["map"]["minLat"]
max_lat = data["map"]["maxLat"]
center_lat = data["map"]["centerLat"]
center_lon = data["map"]["centerLon"]
proximity = data["map"]["proximity"]
random_seed = data["map"]["randomSeed"]
go_to_cost = data["map"]["gotoCost"]
recharge_rate = data["map"]["rechargeRate"]

num_car = data["agents"]["car"]
num_drone = data["agents"]["drone"]
num_boat = data["agents"]["boat"]

speed_drone = data["roles"]["drone"]["speed"]
cap_physical_drone = data["roles"]["drone"]["capacity_physical"]
cap_virtual_drone = data["roles"]["drone"]["capacity_virtual"]
battery_drone = data["roles"]["drone"]["battery"]
photo_ab_drone = data["roles"]["drone"]["abilities"][0]
victim_ab_drone = data["roles"]["drone"]["abilities"][1]
water_ab_drone = data["roles"]["drone"]["abilities"][2]
percieve_drone = data["roles"]["drone"]["percieve"]
kind_drone = data["roles"]["drone"]["kind"]


speed_car = data["roles"]["car"]["speed"]
cap_physical_car = data["roles"]["car"]["capacity_physical"]
cap_virtual_car = data["roles"]["car"]["capacity_virtual"]
battery_car = data["roles"]["car"]["battery"]
photo_ab_car = data["roles"]["car"]["abilities"][0]
victim_ab_car = data["roles"]["car"]["abilities"][1]
water_ab_car = data["roles"]["car"]["abilities"][2]
percieve_car = data["roles"]["car"]["percieve"]
kind_car = data["roles"]["car"]["kind"]


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