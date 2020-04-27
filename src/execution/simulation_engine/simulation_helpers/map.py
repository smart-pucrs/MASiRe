import math
from builtins import list
import logging

import pyroutelib3
import pathlib
from itertools import zip_longest

logger = logging.getLogger(__name__)

class Map:
    """Class that represents the map of the simulation, it holds all the functions about location and the map itself."""

    def __init__(self, map_config, proximity, movement_restrictions):
        map_location = str((pathlib.Path(__file__).parents[4] / map_config['osm']).absolute())
        self.router = pyroutelib3.Router("car", map_location)
        self.measure_unit = 100000
        self.proximity = proximity / self.measure_unit
        self.map_config = map_config
        self.movement_restrictions = movement_restrictions

    def restart(self, map_config, proximity, movement_restrictions):
        """Restart the map by reseting all the variables and also deleting the router from memory to prevent errors.

        :param map_config: The location of the file with the osm map.
        :param proximity: The proximity allowed by the user to someone be considered on the same place as anotherone.
        :param movement_restrictions: Movement restrictions of the environment."""

        del self.router
        map_location = str((pathlib.Path(__file__).parents[4] / map_config['osm']).absolute())
        self.router = pyroutelib3.Router("car", map_location)
        self.measure_unit = 100000
        self.proximity = proximity / self.measure_unit
        self.map_config = map_config
        self.movement_restrictions = movement_restrictions

    def get_closest_node(self, lat, lon):
        """Get the closest node given the latitude and longitude given. It has some errors on the lib itself,
        but not very important like returning the second or third closest node.

        :param lat: The desired latitude.
        :param lon: the desired longitude.
        :return int: The id of the closest node."""

        return self.router.findNode(lat, lon)

    def get_node_coord(self, node):
        """Get the coordinates for the given node.

        :param node: The id of the node.
        :return tuple: The latitude and longitude of the given node."""

        return self.router.nodeLatLon(node)

    def check_location(self, a, b):
        """Check if the location of two objects are considered the same.

        :param a: Location of object a.
        :param b: Location of object b.
        :return bool: True if they are at the same place else False."""
        ax, ay = a
        bx, by = b

        if self.check_proximity(ax, bx):
            if self.check_proximity(ay, by):
                return True

        return False

    def check_proximity(self, a, b):
        """Check if two dots are considered to be at the same place given the proximity.

        :param a: The first dot on the map.
        :param b: The second dot on the map.
        :return bool: True if they are considered to be on the same place else False."""

        if a >= b:
            if a - self.proximity <= b:
                return True

            return False

        if a + self.proximity >= b:
            return True
        return False

    def align_coords(self, lat, lon):
        """Align the coordinates to the ones of the closest node.

        :param lat: The desired latitude.
        :param lon: The desired longitude.
        :return tuple: The location of the closest node."""

        return self.get_node_coord(self.get_closest_node(lat, lon))

    def get_route(self, start_coord, end_coord, abilities, speed, list_of_nodes, events_range):
        """Get the route for each kind of actor.

        For drones and boats, the route is a straight line from one point to another.
        Cars have to respect the nodes on the osm file if none of the nodes are on the list of flooded nodes.

        :param start_coord: The start location.
        :param end_coord: The destination location.
        :param abilities: The kind of the actor, either drone, boat or car.
        :param speed: The speed of the actor.
        :param list_of_nodes: The list of flooded nodes.
        :param events_range: The list of all active events.
        :return tuple: First position containing if the path can be done, second with the list of locations the actor
        must go to get to its destination and the third position hold the distance to the destination."""

        if 'airMovement' in abilities:
            return self.generate_air_route(start_coord, end_coord, speed, events_range)

        elif 'waterMovement' in abilities:
            return self.generate_water_route(start_coord, end_coord, speed, events_range)

        else:
            return self.generate_ground_route(start_coord, end_coord, speed, list_of_nodes)

    def check_node_proximity(self, p1, p2, max_dist):
        """ Check if the two node given is closest, considering the max distance given.

        :param p1: Tuple with the latitude and longitude of the first point.
        :param p2: Tuple with the latitude and longitude of the second point.
        :param max_dist: Float with the max distance allowed.
        :return: True if the two points is close else False.
        """
        return self.euclidean_distance(p1, p2) > max_dist

    def generate_ground_route(self, start_coord, end_coord, speed, list_of_nodes):
        """ Generate route for ground movement.

        Note: The route will considering the speed reduction of events area.

        :param start_coord: Tuple with the latitude and longitude of the start point.
        :param end_coord: Tuple with the latitude and longitude of the end point.
        :param speed: Float that represent the speed of the vehicle.
        :param list_of_nodes: List with all node in event area.
        :return: Tuple with the first element as True if a route are found else False,
                The second have the route end the last have distance between the start coord and the end coord
        """
        reduction = self.movement_restrictions['groundMovement'] / 100 * speed

        start_node = self.get_closest_node(*start_coord)
        end_node = self.get_closest_node(*end_coord)

        result, nodes = self.router.doRoute(start_node, end_node)

        if result == 'no_route':
            return False, [], 0

        elif len(nodes) <= 2:
            if start_node in list_of_nodes:
                return True, self.generate_straight_route(start_coord, end_coord, speed, True), \
                       self.euclidean_distance(start_coord, end_coord)

            return True, self.generate_straight_route(start_coord, end_coord, speed, False), \
                   self.euclidean_distance(start_coord, end_coord)

        route = []
        min_dist = speed / self.measure_unit
        current_node_coord = self.get_node_coord(nodes[0])
        event_area = nodes[0] in list_of_nodes

        for node in nodes[1:-1]:
            node_coord = self.get_node_coord(node)

            if self.is_out(node_coord):
                continue

            if node in list_of_nodes:
                if self.movement_restrictions['groundMovement'] == 100:
                    if route:
                        return True, route, self.euclidean_distance(start_coord, route[-1])
                    else:
                        return False, [], 0

                if not event_area:
                    current_node_coord = node_coord
                    event_area = True
            else:
                if event_area:
                    event_area = False
                    min_route = self.generate_straight_route(current_node_coord, node_coord, speed - reduction, True)
                    
                    route.extend(min_route)
                    current_node_coord = node_coord

                elif self.euclidean_distance(current_node_coord, node_coord) >= min_dist:
                    # min_route = self.generate_straight_route(current_node_coord, node_coord, speed, False)

                    # route.extend(min_route)
                    route.append((*node_coord, False))
                    current_node_coord = node_coord

        if event_area:
            route.extend(self.generate_straight_route(current_node_coord, end_coord, speed - reduction, True))
        else:
            route.extend(self.generate_straight_route(current_node_coord, end_coord, speed, False))

        return True, route, self.euclidean_distance(start_coord, end_coord)

    def generate_air_route(self, start_coord, end_coord, speed, events):
        """ Generate route for air movement.

        Note: The route will considering the speed reduction of events area.

        :param start_coord: Tuple with the latitude and longitude of the start point.
        :param end_coord: Tuple with the latitude and longitude of the end point.
        :param speed: Float that represent the speed of the vehicle.
        :param events: List with all active events.
        :return: Tuple with the first element as True if a route are found else False,
                The second have the route end the last have distance between the start coord and the end coord
        """
        events_in_range = self.filter_events_in_range(start_coord, end_coord, events)
        if not events_in_range:
            return True, self.generate_straight_route(start_coord, end_coord, speed, False), \
                   self.euclidean_distance(start_coord, end_coord)

        restricted_area = self.movement_restrictions['airMovement'] == 100

        t = 0
        route = []
        in_event = False
        current_coord = start_coord
        reduction = self.movement_restrictions['airMovement'] / 100 * speed
        dist_by_step = self.get_straight_factor(start_coord, end_coord, speed)
        dist_with_reduction = 0 if restricted_area else self.get_straight_factor(start_coord, end_coord,
                                                                                 speed - reduction)

        while t < 1:
            if self.check_coord_in_events(current_coord, events):
                in_event = False
                if restricted_area:
                    if route:
                        last_coord = route[-1][:-1]
                        return True, route, self.euclidean_distance(start_coord, last_coord)
                    else:
                        return False, [], 0

                t += dist_with_reduction
            else:
                in_event = True
                t += dist_by_step

            current_coord = (self.straight_equation(start_coord[0], end_coord[0], t),
                             self.straight_equation(start_coord[1], end_coord[1], t),
                             in_event)

            route.append(current_coord)

        if t - 1 < 0:
            route.append((*end_coord, in_event))
        else:
            route[-1] = (*end_coord, in_event)

        return True, route, self.euclidean_distance(start_coord, end_coord)

    def generate_water_route(self, start_coord, end_coord, speed, events):
        """ Generate route for water movement.

        Note: The route will considering the speed reduction of events area.

        :param start_coord: Tuple with the latitude and longitude of the start point.
        :param end_coord: Tuple with the latitude and longitude of the end point.
        :param speed: Float that represent the speed of the vehicle.
        :param events: List with all active events.
        :return: Tuple with the first element as True if a route are found else False,
                The second have the route end the last have distance between the start coord and the end coord
        """
        if self.movement_restrictions['waterMovement'] == 100:
            return False, [], 0

        events_in_range = self.filter_events_in_range(start_coord, end_coord, events)
        if not events_in_range:
            return False, [], 0

        if not self.check_coord_in_events(start_coord, events):
            return False, [], 0

        t = 0
        route = []
        reduction = self.movement_restrictions['waterMovement'] * 0.01 * speed
        dist_per_step = self.get_straight_factor(start_coord, end_coord, speed - reduction)
        current_coord = start_coord

        while t < 1:
            if self.check_coord_in_events(current_coord, events):
                if route:
                    last_coord = route[-1][:-1]
                    return True, route, self.euclidean_distance(start_coord, last_coord)
                else:
                    return False, [], 0

            t += dist_per_step

            current_coord = (self.straight_equation(start_coord[0], end_coord[0], t),
                             self.straight_equation(start_coord[1], end_coord[1], t),
                             True)

            route.append(current_coord)

        return True, route, self.euclidean_distance(start_coord, end_coord)

    def check_coord_in_events(self, coord, events):
        for event in events:
            if self.euclidean_distance(coord, event['location']) < event['radius']:
                return True

        return False

    def get_straight_factor(self, start, end, speed):
        """Calculate the the factor of each step between the start and end point considering the speed.

        Note: This value will be used to calculate a specific line coordinate between the two points.

        :param start: Tuple with the latitude and longitude of the start point.
        :param end: Tuple with the latitude and longitude of the end point.
        :param speed: The velocity of the vehicle.
        """
        return 1 / ((self.euclidean_distance(start, end) * self.measure_unit) / speed)

    def filter_events_in_range(self, start_coord, end_coord, events):
        """ Filter all events that will intersect the route.

        Note: considering a straight route.

        :param start_coord: Tuple with the latitude and longitude of the start point.
        :param end_coord: Tuple with the latitude and longitude of the end point.
        :param events: List with all active events.
        :return: List with the events that intersect the route
        """
        events_in_range = []

        for event in events:
            if self.euclidean_distance(start_coord, event['location']) < event['radius']:
                events_in_range.append(event)

            elif self.euclidean_distance(end_coord, event['location']) < event['radius']:
                events_in_range.append(event)

        return events_in_range

    def nodes_in_radius(self, coord, radius):
        """Get all the nodes in a circle around the coordinate given.

        :param coord: Central coordinate.
        :param radius: The radius of the circle.
        :return list: List of all the nodes inside the circle."""

        result = []
        for node in self.router.rnodes:
            node_coord = self.get_node_coord(node)
            if self.euclidean_distance(node_coord, coord) <= radius:
                if not self.is_out(node_coord):
                    result.append(node)
        return result

    def is_out(self, node):
        result = False
        if node[0] <= self.map_config['minLat']:
            result = True
        elif node[0] >= self.map_config['maxLat']:
            result = True
        elif node[1] <= self.map_config['minLon']:
            result = True
        elif node[1] >= self.map_config['maxLon']:
            result = True

        return result

    def node_to_radian(self, node):
        """Convert the node location to radian coordinate.

        :param node: The node id.
        :return list: Radians location for the given node."""

        return self.coords_to_radian(self.router.nodeLatLon(node))

    def node_distance(self, node_x, node_y):
        """Get the distance between two nodes.

        :param node_x: The first node id.
        :param node_y: The second node id.
        :return float: The distance between two nodes."""

        return self.router.distance(self.node_to_radian(node_x), self.node_to_radian(node_y))

    def generate_straight_route(self, start, end, speed, event_area):
        """ Generate a straight route between the start coord to the end coord using the speed in each step.

        :param start: Tuple with the latitude and longitude of the start point.
        :param end: Tuple with the latitude and longitude of the end point.
        :param speed: Float that represent the speed of the vehicle.
        :param event_area: Bool with True if the straight is in event area else False.
        :return: List with the route from start coord and end coord.
        """
        x_start, y_start = start
        x_end, y_end = end

        route = []
        points_amount = round((self.euclidean_distance(start, end) * self.measure_unit) / speed)

        if not points_amount:
            return [(*end,event_area)]

        unit = 1 / points_amount

        for i in range(1, points_amount + 1):
            route.append((self.straight_equation(x_start, x_end, i * unit),
                          self.straight_equation(y_start, y_end, i * unit),
                          event_area))

        return route

    @staticmethod
    def straight_equation(x, y, t):
        """ Calculate the point value of the straight equation.

        :param x: Float represent the first point.
        :param y: Float represent the second point.
        :param t: Float represent the local of the straight, 0 to 1
        :return: Float represent the value of the straight equation in the point t.
        """
        return x * (1 - t) + y * t

    @staticmethod
    def euclidean_distance(a, b):
        """Calculate the euclidean distance between two locations."""

        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    @staticmethod
    def coords_to_radian(coords):
        """Convert coordinates to radians."""

        return list(map(math.radians, coords))
