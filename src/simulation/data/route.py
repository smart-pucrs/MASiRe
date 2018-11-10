# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Route.java
import math
from pyroutelib3 import Router as py_router # Import the router
from src.simulation.data.events.flood import Flood

class Route:

    def __init__(self, map):
        self.router = py_router("car", map)                 # Initialise router object from pyroutelib3
        self.original_state = self.router.routing.copy()    # Copies the baseline routing table that pyroutelib3 created
        self.routing_states = [self.original_state.copy()]  # Initializes list of state changes with original state only

    def get_closest_node(self, lat, lon):
        return self.router.findNode(lat, lon)

    def get_node_coord(self, node):
        return self.router.nodeLatLon(node)

    def align_coords(self, lat, lon):
        return self.get_node_coord(self.get_closest_node(lat, lon))

    def generate_routing_tables(self, events):
        # Resulting list of routing state changes on each step
        routing_states = [None for _ in range(len(events))]

        # In which steps should the routing table be recalculated
        recalculate_at = [False for _ in range(len(events))]

        # Floods existing at the specified step
        floods_during = [[] for _ in range(len(events))]

        for curr_step, curr_flood in enumerate(events):
            if type(curr_flood) is Flood:
                # Adds this step's flood to curr_floods, repeating it until it's disappearance
                for i in range(curr_step, curr_step + curr_flood.period):
                    if(len(floods_during) > i):
                        print("---------------------------i: ", i, " -------------------------------------")
                        floods_during[i].append(curr_flood)

                # Register change events on flood's appearance and disappearance steps
                recalculate_at[curr_step] = True
                if curr_step + curr_flood.period < len(events):
                    recalculate_at[curr_step + curr_flood.period] = True

            print('----------------------------')
            print(curr_flood)
            print(recalculate_at)
            print('----------------------------')

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

        print('End of routing tables creation')
        print(routing_states)

    def update_routing(self, step):
        if type(self.routing_states[step]) is not None:
            self.router.routing = self.routing_states[step].copy()

    def do_route(self):
        pass

    def nodes_in_radius(self, coord, radius):
        # radius in kilometers
        result = []
        for node in self.router.rnodes:
            if self.router.distance(self.node_to_radian(node), self.coords_to_radian(coord)) <= radius:
                result.append(node)
        return result

    def node_to_radian(self, node):
        """Returns the radian coordinates of a given OSM node"""
        return self.coords_to_radian(self.router.nodeLatLon(node))

    def coords_to_radian(self, coords):
        """Maps a coordinate from degrees to radians"""
        return list(map(math.radians, coords))

    def remove_nodes(self, nodes_to_remove, routing):
        """Removes the specified nodes from the routing table"""
        for node in nodes_to_remove:
            routing.pop(node, None)

        for node in routing:
            for connection in nodes_to_remove:
                routing[node].pop(connection, None)
                if len(routing[node]) == 0:
                    break

        return routing



