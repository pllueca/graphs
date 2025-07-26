from .base_graph import Graph


### Graph traversal
def graph_traversal_dfs(g: Graph, start_node: int) -> list[int]:
    """Traverse the graph depth first starting at start_node.
    return the list of visited nodes."""

    # DFS non-recursive.
    # for each step, get neighbor, visit, return
    # do not repeat nodes. there may be cycles!
    visited_nodes = set()
    to_visit_stack = [start_node]

    while to_visit_stack:
        current = to_visit_stack.pop()
        # avoid repeating nodes
        if current in visited_nodes:
            continue

        visited_nodes.add(current)
        for neighbor in g.adjacency_list[current]:
            to_visit_stack.append(neighbor)
    return list(visited_nodes)


def is_connected(g: Graph) -> bool:
    """Return true if g is a single connext component, False otherwise.

    If starting from any edge we can see every other, it is connected."""
    return len(graph_traversal_dfs(g, 0)) == g.size
