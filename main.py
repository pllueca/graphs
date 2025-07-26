from lib.undirected_graph import (
    UndirectedGraph,
)
from lib.directed_graph import DirectedGraph
from lib.common import graph_traversal_dfs, is_connected
from lib.visualization import draw_graph, draw_directed_graph

### tests


def traversals():
    # undirectected tree
    g = UndirectedGraph.from_edge_list(
        n=7,
        edges=[
            (0, 1),
            (1, 2),
            (2, 3),
            (2, 4),
            (4, 5),
            (2, 6),
        ],
    )
    print(g.adjacency_list, g.is_tree)
    print(g.graph_traversal_dfs(0))
    print(g.is_connected())

    print(g.graph_traversal_bfs(2))  # 2, 1, 3, 4, 6, 0, 5
    print(g.graph_traversal_dfs(2))  # 2, 1, 0, 3, 4, 5, 6

    ### undirected, 2 connected components
    g = UndirectedGraph.from_edge_list(
        n=10,
        edges=[
            (0, 1),
            (1, 2),
            (2, 3),
            (2, 4),
            (4, 5),
            (2, 6),
            (7, 8),
            (7, 9),
            (8, 9),
        ],
    )
    print(g)
    print(g.is_connected())

    for sg in g.connected_components():
        print(sg, sg.is_tree())
    print(g.is_tree())


def cycles():
    g = DirectedGraph.from_edge_list(
        5,
        [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4)],
    )
    print(g)
    print(g.topological_order())

    # with cycles
    g = DirectedGraph.from_edge_list(
        5,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (1, 4),
            (3, 4),  # no cycles up to here
            (3, 0),  # Creates a cycle
        ],
    )
    print(g)
    print(g.topological_order())
    # print(g, g.has_cycles())


def visualize_graph():
    g = DirectedGraph.from_edge_list(
        5,
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (1, 4),
            (3, 4),  # no cycles up to here
            (3, 0),  # Creates a cycle
        ],
    )
    draw_graph(g)
    draw_directed_graph(g)
    print("done")


# cycles()
visualize_graph()
