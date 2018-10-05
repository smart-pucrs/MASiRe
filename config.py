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


speed_boat = data["roles"]["boat"]["speed"]
cap_physical_boat = data["roles"]["boat"]["capacity_physical"]
cap_virtual_boat = data["roles"]["boat"]["capacity_virtual"]
battery_boat = data["roles"]["boat"]["battery"]
photo_ab_boat = data["roles"]["boat"]["abilities"][0]
victim_ab_boat = data["roles"]["boat"]["abilities"][1]
water_ab_boat = data["roles"]["boat"]["abilities"][2]
percieve_boat = data["roles"]["boat"]["percieve"]
kind_boat = data["roles"]["boat"]["kind"]


quad_size = data["generate"]["quadSize"]
flood_probability = data["generate"]["floodProbability"]

flood_min_period = data["generate"]["flood"]["minPeriod"]
flood_max_period = data["generate"]["flood"]["maxPeriod"]

circle_min_rad = data["generate"]["flood"]["circle"]["minRadius"]
circle_max_rad = data["generate"]["flood"]["circle"]["maxRadius"]

rect_min_height = data["generate"]["flood"]["rectangle"]["minHeight"]
rect_max_height = data["generate"]["flood"]["rectangle"]["minHeight"]
rect_min_length = data["generate"]["flood"]["rectangle"]["minLength"]
rect_max_length = data["generate"]["flood"]["rectangle"]["maxLength"]

photo_size = data["generate"]["photo"]["size"]
photo_min_amount = data["generate"]["photo"]["minAmount"]
photo_max_amount = data["generate"]["photo"]["maxAmount"]
photo_victim_prob = data["generate"]["photo"]["victimProbability"]

victim_min_size = data["generate"]["victim"]["minSize"]
victim_max_size = data["generate"]["victim"]["maxSize"]
victim_min_amount = data["generate"]["victim"]["minAmount"]
victim_max_amount = data["generate"]["victim"]["maxAmount"]
victim_min_lifetime = data["generate"]["victim"]["minLifetime"]
victim_max_lifetime = data["generate"]["victim"]["maxLifetime"]

water_sample_size = data["generate"]["waterSample"]["size"]
water_sample_min = data["generate"]["waterSample"]["minAmount"]
water_sample_max = data["generate"]["waterSample"]["maxAmount"]

#print(quad_size)