import math
import pyroutelib3
import pathlib
from itertools import zip_longest


class Map:
    """Class that represents the map of the simulation, it holds all the functions about location and the map itself."""

    def __init__(self, map_location, proximity):
        map_location = str((pathlib.Path(__file__).parents[4] / map_location).absolute())
        self.router = pyroutelib3.Router("car", map_location)
        self.proximity = proximity/1000

    def restart(self, map_location, proximity):
        """Restart the map by reseting all the variables and also deleting the router from memory to prevent errors.

        :param map_location: The location of the file with the osm map.
        :param proximity: The proximity allowed by the user to someone be considered on the same place as anotherone."""

        del self.router
        map_location = str((pathlib.Path(__file__).parents[4] / map_location).absolute())
        self.router = pyroutelib3.Router("car", map_location)
        self.proximity = proximity/1000

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

    def get_route(self, start_coord, end_coord, role, speed, list_of_nodes):
        """Get the route for each kind of actor.

        For drones and boats, the route is a straight line from one point to another.
        Cars have to respect the nodes on the osm file if none of the nodes are on the list of flooded nodes.

        :param start_coord: The start location.
        :param end_coord: The destination location.
        :param role: The kind of the actor, either drone, boat or car.
        :param speed: The speed of the actor.
        :param list_of_nodes: The list of flooded nodes.
        :return tuple: First position containing if the path can be done, second with the list of locations the actor
        must go to get to its destination and the third position hold the distance to the destination."""

        if role == 'drone':
            return self.generate_coordinates_for_drones(start_coord, end_coord, speed)

        elif role == 'boat':
            return self.generate_coordinates_for_boats(start_coord, end_coord, speed, list_of_nodes)

        else:
            start_node = self.get_closest_node(*start_coord)
            end_node = self.get_closest_node(*end_coord)
            if start_node not in list_of_nodes:
                result, nodes = self.router.doRoute(start_node, end_node)

                if result == 'no_route':
                    return False, [], 0

                checked_nodes = []
                for node in nodes:
                    if node in list_of_nodes:
                        return False, [], 0

                    checked_nodes.append(self.get_node_coord(node))

                return True, checked_nodes, self.node_distance(start_node, end_node)

            return False, [], 0

    def nodes_in_radius(self, coord, radius):
        """Get all the nodes in a circle around the coordinate given.

        :param coord: Central coordinate.
        :param radius: The radius of the circle.
        :return list: List of all the nodes inside the circle."""

        result = []
        for node in self.router.rnodes:
            if self.router.distance(self.node_to_radian(node), self.coords_to_radian(coord)) <= radius:
                result.append(node)
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

    def generate_coordinates_for_drones(self, start, end, speed):
        """Generate a straight line connecting two locations.

        :param start: The start location.
        :param end: The destination location.
        :param speed: The speed of the drone.
        :return tuple: First position holding True if there is a path else False, second position holding the list with
        all the locations the drone have to go to reach the destination and the thirhd position with the euclidean
        distance between the two locations."""

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

        return True, list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance

    def generate_coordinates_for_boats(self, start, end, speed, list_of_nodes=None):
        """Generate a straight line connecting two locations.

        Note: A boat can only move through flooded nodes.

        :param start: The start location.
        :param end: The destination location.
        :param speed: The speed of the boat.
        :param list_of_nodes: List of all the flooded nodes.
        :return tuple: First position holding True if there is a path else False, second position holding the list with
        all the locations the drone have to go to reach the destination and the thirhd position with the euclidean
        distance between the two locations."""

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

                return True, list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance
        return False, [], 0

    def decrease_until_reached(self, start, end, speed, list_of_nodes=None):
        """Generate a list of points from one point to another.

        This method will decrease the start point until it is considered to be equal to the end point.

        :param start: The start point.
        :param end: The end point.
        :param speed: The speed of the actor.
        :param list_of_nodes: The list of the flooded nodes for boats.
        :return list|None: List of all the points until reaching the destination."""

        if start == end:
            return [end]

        points = []
        while True:
            if start - .0005 * speed <= end:
                points.append(end)
                break
            else:
                start -= .0005 * speed

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
        """Generate a list of points from one point to another.

        This method will increase the start point until it is considered to be equal to the end point.

        :param start: The start point.
        :param end: The end point.
        :param speed: The speed of the actor.
        :param list_of_nodes: The list of the flooded nodes for boats.
        :return list|None: List of all the points until reaching the destination."""

        if start == end:
            return [end]

        points = []
        while True:
            if start + .0005 * speed >= end:
                points.append(end)
                break
            else:
                start += .0005 * speed

            if list_of_nodes:
                node = self.get_closest_node(start, end)
                if node in list_of_nodes:
                    points.append(start)
                else:
                    return None
            else:
                points.append(start)

        return points

    @staticmethod
    def euclidean_distance(a, b):
        """Calculate the euclidean distance between two locations."""

        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    @staticmethod
    def coords_to_radian(coords):
        """Convert coordinates to radians."""

        return list(map(math.radians, coords))
