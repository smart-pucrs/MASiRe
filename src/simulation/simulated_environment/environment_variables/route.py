# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Route.java
import math
from pyroutelib3 import Router
from itertools import zip_longest
from directory_path import dir as root


class Route:

    def __init__(self, map_name, proximity):
        map_file_location = root / map_name
        self.router = Router("car", str(map_file_location))
        self.proximity = proximity

    def get_closest_node(self, lat, lon):
        """
        [Gets the closest node to a given coordinate on the map]
        :param lat: Latitude
        :param lon: Longitude
        :return: The closest node id
        """
        return self.router.findNode(lat, lon)

    def get_node_coord(self, node):
        """
        [Maps a node id to a polar coordinate]
        :param node: The given node
        :return: This node's coordinates
        """
        return self.router.nodeLatLon(node)

    def align_coords(self, lat, lon):
        """
        [Maps a coordinate to the coordinate of the closest node]
        :param lat: Latitude
        :param lon: Longitude
        :return: A new coordinate corresponding to the location of the closest node
        """
        return self.get_node_coord(self.get_closest_node(lat, lon))

    def get_route(self, start, end, role, speed=4, list_of_nodes=None):
        if role == 'drone':
            return self.generate_coordinates_for_drones(start, end, speed)
        elif role == 'boat':
            return self.generate_coordinates_for_boats(start, end, speed, list_of_nodes)

        if start not in list_of_nodes:
            coords = []
            result, nodes = self.router.doRoute(start, end)
            for node in nodes:
                if node not in list_of_nodes:
                    coords.append(list(self.get_node_coord(node)))
                else:
                    return "no_route", []
            return result, coords

        return "no_route", []

    def nodes_in_radius(self, coord, radius):
        """
        [Finds the nodes within a certain radius of the given coordinate]
        :param coord: The central coordinate of the circle
        :param radius: The radius of the circle, in kilometers
        :return: A list of node ids that are inside the circle area
        """
        result = []
        for node in self.router.rnodes:
            if self.router.distance(self.node_to_radian(node), self.coords_to_radian(coord)) <= radius:
                result.append(node)
        return result

    def node_to_radian(self, node):
        """
        [Maps a node to it's radian coordinates]
        :param node: The node id
        :return: The radian coordinates of a given OSM node
        """
        return self.coords_to_radian(self.router.nodeLatLon(node))

    def coords_to_radian(self, coords):
        """
        [Maps a coordinate from degrees to radians]
        :param coords: A set of polar coordinates
        :return: A set of radian coordinates
        """
        return list(map(math.radians, coords))

    def node_distance(self, node_x, node_y):
        """
        [Calculates the distance between two nodes]
        :param node_x: The first node
        :param node_y: The second node
        :return: The straight line distance in kilometers between two given OSM nodes
        """
        return self.router.distance(self.node_to_radian(node_x), self.node_to_radian(node_y))

    def generate_coordinates_for_drones(self, start, end, speed):
        actual_x, actual_y = start

        if actual_x > end[0]:
            x_axis = self.decrease_until_reached(actual_x, end[0], speed) or [end[0]]
        else:
            x_axis = self.increase_until_reached(actual_x, end[0], speed) or [end[0]]

        if actual_y > end[1]:
            y_axis = self.decrease_until_reached(actual_y, end[1], speed) or [end[1]]
        else:
            y_axis = self.increase_until_reached(actual_y, end[1], speed) or [end[1]]

        longest = y_axis[-1] if len(x_axis) > len(y_axis) else x_axis[-1]
        distance = self.router.distance(self.coords_to_radian(start), self.coords_to_radian(end))

        return list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance

    def generate_coordinates_for_boats(self, start, end, speed, list_of_nodes=None):
        start_node = self.get_closest_node(*start)
        end_node = self.get_closest_node(*end)

        if start_node in list_of_nodes:
            if end_node in list_of_nodes:
                actual_x, actual_y = start

                if actual_x > end[0]:
                    x_axis = self.decrease_until_reached(actual_x, end[0], speed, list_of_nodes) or [end[0]]
                else:
                    x_axis = self.increase_until_reached(actual_x, end[0], speed, list_of_nodes) or [end[0]]

                if actual_y > end[1]:
                    y_axis = self.decrease_until_reached(actual_y, end[1], speed, list_of_nodes) or [end[1]]
                else:
                    y_axis = self.increase_until_reached(actual_y, end[1], speed, list_of_nodes) or [end[1]]

                longest = y_axis[-1] if len(x_axis) > len(y_axis) else x_axis[-1]
                distance = self.router.distance(self.coords_to_radian(start), self.coords_to_radian(end))

                return list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance
        return [], 0

    def decrease_until_reached(self, start, end, speed, list_of_nodes=None):
        if start == end:
            return [end]

        points = []
        while True:
            if start - self.proximity * speed < end:
                points.append(end)
                break
            else:
                start -= self.proximity * speed

            if list_of_nodes:
                node = self.get_closest_node(start, end)
                if node in list_of_nodes:
                    points.append(start)
                else:
                    return None
            else:
                points.append(start)

        return points

    def increase_until_reached(self, start, end, speed, list_of_nodes=None):
        if start == end:
            return [end]

        points = []
        while True:
            if start + self.proximity * speed > end:
                points.append(end)
                break
            else:
                start += self.proximity * speed

            if list_of_nodes:
                node = self.get_closest_node(start, end)
                if node in list_of_nodes:
                    points.append(start)
                else:
                    return None
            else:
                points.append(start)

        return points
