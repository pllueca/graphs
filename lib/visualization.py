"""
https://stackoverflow.com/questions/20133479/how-to-draw-directed-graphs-using-networkx-in-python
"""

import networkx as nx
import matplotlib.pyplot as plt

from .base_graph import Graph
from .directed_graph import DirectedGraph


def draw_graph(g: Graph):
    nx_graph = nx.Graph()
    nx_graph.add_nodes_from(g.nodes)
    nx_graph.add_edges_from(g.edges)
    pos = nx.spring_layout(nx_graph)
    nx.draw_networkx_nodes(nx_graph, pos)
    nx.draw_networkx_edges(nx_graph, pos)
    nx.draw_networkx_labels(nx_graph, pos)
    plt.show()


def draw_directed_graph(g: DirectedGraph):
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(g.nodes)
    nx_graph.add_edges_from(g.edges)
    pos = nx.spring_layout(nx_graph)
    nx.draw_networkx_nodes(nx_graph, pos)
    nx.draw_networkx_labels(nx_graph, pos)
    nx.draw_networkx_edges(nx_graph, pos, arrows=True)
    plt.show()
