import json
import math
from pathlib import Path

from core.navigator import Navigator
from core.td_graph import Edge, Node, TDGraph


def resolve_vertex_index(key, graph):
    key_str = str(key)
    for i in range(len(graph.nodes)):
        if graph.nodes[i].key == key_str:
            return i
    return -1


def load_graph(nodes_path, edges_path):
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)
    with nodes_path.open("r", encoding="utf-8") as f:
        nodes_data = json.load(f)
    with edges_path.open("r", encoding="utf-8") as f:
        edges_data = json.load(f)

    graph = TDGraph()
    types = {}

    for i in range(len(nodes_data)):
        nd = nodes_data[i]
        node = Node(i, nd["id"], nd["name"], nd["x"], nd["y"])
        graph.addNode(node)
        types[str(nd["id"])] = nd.get("type", "Waypoint")

    for ed in edges_data:
        u = resolve_vertex_index(ed["from"], graph)
        v = resolve_vertex_index(ed["to"], graph)
        if u == -1 or v == -1:
            continue
        x1, y1 = graph.nodes[u].x, graph.nodes[u].y
        x2, y2 = graph.nodes[v].x, graph.nodes[v].y
        weight = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        graph.addEdge(Edge(u, v, weight))
        if ed.get("bidirectional", True):
            graph.addEdge(Edge(v, u, weight))

    return graph, Navigator(graph), types
