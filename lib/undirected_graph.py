from dataclasses import dataclass
from collections import defaultdict

from .base_graph import Graph


@dataclass
class UndirectedGraph(Graph):

    @classmethod
    def from_edge_list(cls, n: int, edges: list[tuple[int, int]]):
        """Construct a graph from a list of edges.

        since its undirected, an edge ai-bi implies that bi-ai is also connected"""
        nodes = set(range(n))
        adjacency_list = {n: [] for n in nodes}
        for source, dest in edges:
            adjacency_list[source].append(dest)
            adjacency_list[dest].append(source)

        return cls(nodes=nodes, adjacency_list=dict(adjacency_list))

    def num_edges(self) -> int:
        edges = 0
        for source, list_of_dest in self.adjacency_list.items():
            for dest in list_of_dest:
                if source > dest:
                    edges += 1
        return edges

    def is_tree(self) -> bool:
        """
        a graph is a tree if the number of edges of each connected component is size of component - 1
        """
        for g in self.connected_components():
            if g.num_edges() > (g.size - 1):
                return False
        return True
