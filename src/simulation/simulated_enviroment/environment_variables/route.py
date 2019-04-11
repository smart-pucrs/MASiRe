# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Route.java
import math
import directory_path as root
from pyroutelib3 import Router


class Route:

    def __init__(self, map):
        map_file_location = root.dir + '/' + map
        self.router = Router("car", map_file_location)      # Initialise router object from pyroutelib3
        self.original_state = self.router.routing.copy()    # Copies the baseline routing table that pyroutelib3 created
        self.routing_states = [self.original_state.copy()]  # Initializes list of state changes with original state only

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

    def generate_routing_tables(self, events):
        """
        [Generates the routing tables that will be part of the simulation. A routing table is present in the list every
        time a flood start or ends]
        :param events: A list of steps, each with a list of floods that will appear during each step
        :return: Sets up the routing_states class variable with a list of steps and each routing state update when
        changes are detected
        """
        # Resulting list of routing state changes on each step
        routing_states = [None] * len(events)

        # In which steps should the routing table be recalculated
        recalculate_at = [False] * len(events)

        # Floods existing at the specified step
        floods_during = [[]] * len(events)

        for curr_step, curr_flood in enumerate(events):
            if curr_flood is None:
                continue

            # Adds this step's flood to curr_floods, repeating it until it's disappearance
            for i in range(curr_step, curr_step + curr_flood.period):
                if len(floods_during) > i:
                    floods_during[i].append(curr_flood)

            # Register change events on flood's appearance and disappearance steps
            recalculate_at[curr_step] = True
            if curr_step + curr_flood.period < len(events):
                recalculate_at[curr_step + curr_flood.period] = True

            # Were there changes in flood locations in this step?
            if recalculate_at[curr_step]:
                # Aggregates nodes affected by each flood during this step
                affected_nodes = []

                for flood in floods_during[curr_step]:
                    for node in self.nodes_in_radius(flood.dimensions["coord"], flood.dimensions["radius"]):
                        affected_nodes.append(node)

                removed_map = self.original_state.copy()
                self.remove_nodes(affected_nodes, removed_map)  # Removes flooded nodes from baseline copy
                routing_states[curr_step] = removed_map         # Record new state and at which step it occurred

        self.routing_states = routing_states

    def update_routing(self, step):
        """
        [Updates the routing table that will be used for routing in a given step]
        :param step: Which simulation step should be considered for routing
        :return: Sets up the router.routing class variable that will be used for routing
        """
        if self.routing_states[step] is not None:
            self.router.routing = self.routing_states[step].copy()

    def do_route(self, route, distance):
        """
        [Attempts to travel up to a certain distance along the given route]
        :param route: The list of node ids that make up the route
        :param distance: The distance to be travelled, in kilometers
        :return: The resulting node's ID and coordinate and the actual distance travelled
        """
        acc = 0  # initially has travelled 0 km
        final_location = route[0]  # start of route is initial location
        for i in range(len(route) - 1):
            curr_distance = self.node_distance(route[i], route[i + 1])

            if acc + curr_distance > distance:  # if trying to walk more than the maximum defined value
                return final_location, self.router.nodeLatLon(final_location), acc  # then stop at current node
            acc += curr_distance  # was able to walk further along
            final_location = route[i + 1]  # new location
        return final_location, self.router.nodeLatLon(final_location), acc  # reached the end of the route

    def total_route_length(self, route):
        """
        [Calculates the total length of route, from node to node and then prints it]
        :param route:
        :return: Prints the total distance of the route
        """
        route_lat_lons = list(map(self.router.nodeLatLon, route))  # Get actual route coordinates
        distances = []

        for i in range(len(route_lat_lons) - 1):
            print("From: %s" % route[i])
            print("To: %s" % route[i + 1])
            distance = self.router.distance(self.coords_to_radian(route_lat_lons[i]), self.coords_to_radian(route_lat_lons[i + 1]))

            print("%.2fm" % (distance * 1000))
            print('-----------------')

            distances.append(distance)

        print("Total: %.2fm" % (math.fsum(distances) * 1000))

    def get_route(self, start, end):
        #self.router.
        pass

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

    def remove_nodes(self, nodes_to_remove, routing):
        """
        [Removes the specified nodes from the routing table]
        :param nodes_to_remove: A list of nodes to be removed
        :param routing: The routing table from which to remove them
        :return: The updated routing table without the nodes specified
        """
        for node in nodes_to_remove:
            routing.pop(node, None)

        for node in routing:
            for connection in nodes_to_remove:
                routing[node].pop(connection, None)
                if len(routing[node]) == 0:
                    break

        return routing



