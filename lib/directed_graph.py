from dataclasses import dataclass
from collections import defaultdict

from .base_graph import Graph


@dataclass
class DirectedGraph(Graph):

    @classmethod
    def from_edge_list(cls, n: int, edges: list[tuple[int, int]]):
        """Construct a graph from a list of edges."""

        adjacency_list = {node: [] for node in range(n)}
        for source, dest in edges:
            adjacency_list[source].append(dest)

        return cls(nodes=set(range(n)), adjacency_list=dict(adjacency_list))

    def num_edges(self) -> int:
        edges = 0
        for _, list_of_dest in self.adjacency_list.items():
            for _ in list_of_dest:
                edges += 1
        return edges

    def has_cycles(self) -> bool:
        """Return True if the graph contains cycles"""
        # for each node, do a dfs search. if at any moment we arrivee at the starting node, return true
        # nodes contain the nodes that has not been explored
        # if a node is not in nodes, means that there are no cycles from there on.
        # if when traversing we find a node that is not in nodes, we dont have to explore the graph from there, since we have already done it.
        remaining_nodes = self.nodes.copy()
        for node in self.nodes:
            current_path = set()
            to_visit = [node]
            while to_visit:
                current = to_visit.pop()
                # we are back at the start, there is a cycle
                if current == node:
                    return True

                # we have explored the graph from this node at some point, and there is are no cycles
                # if current not in remaining_nodes:
                # continue

                current_path.add(current)
                for neighbor in self.adjacency_list[current]:
                    to_visit.append(neighbor)

            # we explored the graph starting from node and found no cycles
            remaining_nodes.difference_update(current_path)
        return False

    def topological_order(self) -> list[int]:
        """Return an ordering of nodes where every node appears before the nodes it points to.

        Asume the graph is a single connected component and acyclic."""

        # algorithm
        # keep track of the "inverse" of the adjacency list, i.e. which nodes point to each node.
        # iteratively, find a node with 0 inflow (0 nodes point it to it). add it to the ordering, and remove the edges to where it points.

        # compute inverse adjacency
        # node_id: set of nodes it points too
        inflow_list = {node: set() for node in self.nodes}
        for node in self.nodes:
            for neighbor in self.adjacency_list[node]:
                # node points to neighbor
                inflow_list[neighbor].add(node)

        ordering = []
        while inflow_list:
            # find node with 0 inflow, add to ordering, remove
            node_0_inflow = None
            for node, inflow in inflow_list.items():
                if not inflow:
                    node_0_inflow = node
                    break
            if node_0_inflow is None:
                raise Exception(
                    "Graph has cycles"
                )  # we havent found any node with 0 inflow. cycles!

            ordering.append(node_0_inflow)
            # remove node from the remaining, and its connections
            del inflow_list[node_0_inflow]
            for neighbor in self.adjacency_list[node_0_inflow]:
                inflow_list[neighbor].remove(node_0_inflow)

        return ordering
