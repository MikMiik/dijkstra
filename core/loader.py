import json
import math
from pathlib import Path

from core.navigator import Navigator
from core.graph import Edge, Graph, Node


def load_graph(nodes_path, edges_path):
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)
    with nodes_path.open("r", encoding="utf-8") as f:
        nodes_data = json.load(f)
    with edges_path.open("r", encoding="utf-8") as f:
        edges_data = json.load(f)

    graph = Graph()
    types = {}

    for i in range(len(nodes_data)):
        nd = nodes_data[i]
        node = Node(i, nd["name"], nd["x"], nd["y"])
        graph.addNode(node)
        types[i] = nd.get("type", "Waypoint")

    node_count = len(graph.nodes)
    for ed in edges_data:
        u = int(ed["from"])
        v = int(ed["to"])
        if u < 0 or u >= node_count or v < 0 or v >= node_count:
            continue
        x1, y1 = graph.nodes[u].x, graph.nodes[u].y
        x2, y2 = graph.nodes[v].x, graph.nodes[v].y
        weight = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        graph.addEdge(Edge(u, v, weight))
        if ed.get("bidirectional", True):
            graph.addEdge(Edge(v, u, weight))

    return graph, Navigator(graph), types
