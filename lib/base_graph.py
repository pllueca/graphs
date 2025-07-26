from typing import TypeVar
from dataclasses import dataclass
from collections import OrderedDict

T = TypeVar("T", bound="Graph")


@dataclass
class Graph:
    nodes: set[int]
    adjacency_list: dict[int, list[int]]

    @property
    def size(self) -> int:
        return len(self.nodes)

    @property
    def edges(self) -> list[tuple[int, int]]:
        edges = []
        for n in self.nodes:
            for other in self.adjacency_list[n]:
                edges.append((n, other))
        return edges

    def __repr__(self) -> str:
        return f"<{self.__class__}, nodes:{self.nodes}, adjacencies: {self.adjacency_list}>"

    ### Graph traversal
    def graph_traversal_dfs(self, start_node: int) -> list[int]:
        """Traverse the graph depth first starting at start_node.
        return the list of visited nodes."""

        # DFS non-recursive.
        # for each step, get neighbor, visit, return
        # do not repeat nodes. there may be cycles!
        visited_nodes = (
            OrderedDict()
        )  # we want to keep the order of the visited nodes, but also quick check for already visiteed
        to_visit_stack = [start_node]

        while to_visit_stack:
            current = to_visit_stack.pop()
            # avoid repeating nodes
            if current in visited_nodes:
                continue
            # just adding the key to the dict, we dont care about value
            visited_nodes[current] = 0
            for neighbor in self.adjacency_list[current]:
                to_visit_stack.append(neighbor)
        return list(visited_nodes)

    def graph_traversal_bfs(self, start_node: int) -> list[int]:
        """Traverse the graph breadth first starting at start_node.
        return the list of visited nodes."""

        # BFS non-recursive.
        # do not repeat nodes. there may be cycles!
        visited_nodes = OrderedDict()
        to_visit_queue = [start_node]

        while to_visit_queue:
            current = to_visit_queue.pop()
            # avoid repeating nodes
            if current in visited_nodes:
                continue

            visited_nodes[current] = 0
            for neighbor in self.adjacency_list[current]:
                to_visit_queue.insert(0, neighbor)
        return list(visited_nodes)

    def is_connected(self) -> bool:
        """Return true if g is a single connext component, False otherwise.

        If starting from any edge we can see every other, it is connected."""
        return len(self.graph_traversal_dfs(0)) == self.size

    @classmethod
    def from_edge_list(cls: type[T], n: int, edges: list[tuple[int, int]]) -> T:
        raise NotImplementedError("Subclasses must implement")

    def subgraph_from_nodes(self: T, nodes: list[int]) -> T:
        new_adjacency = {}
        for n in nodes:
            new_adjacency[n] = self.adjacency_list[n].copy()
        return self.__class__(set(nodes), new_adjacency)

    def connected_components(self: T) -> list[T]:
        """Return a list of Graphs, each represented a connected component of self.
        if self.is_connected, then self.connectec_components == [self]"""
        components: list[T] = []
        # need to use all this nodes
        nodes = self.nodes.copy()
        while nodes:
            current_start = nodes.pop()
            nodes_in_component = self.graph_traversal_dfs(current_start)
            # build graph from nodes_in_component
            components.append(self.subgraph_from_nodes(nodes_in_component))
            nodes.difference_update(nodes_in_component)
        return components
