import math

from core.graph import Edge, Graph, Node
from core.navigator import Navigator


def build_grid_graph(side):
    graph = Graph()
    for row in range(side):
        for col in range(side):
            node_id = row * side + col
            graph.addNode(Node(node_id, f"G{node_id}", col, row, "Waypoint"))

    for row in range(side):
        for col in range(side):
            node_id = row * side + col
            if col + 1 < side:
                right = row * side + col + 1
                weight = math.sqrt((graph.nodes[right].x - graph.nodes[node_id].x) ** 2 + (graph.nodes[right].y - graph.nodes[node_id].y) ** 2)
                graph.addEdge(Edge(node_id, right, weight))
                graph.addEdge(Edge(right, node_id, weight))
            if row + 1 < side:
                down = (row + 1) * side + col
                weight = math.sqrt((graph.nodes[down].x - graph.nodes[node_id].x) ** 2 + (graph.nodes[down].y - graph.nodes[node_id].y) ** 2)
                graph.addEdge(Edge(node_id, down, weight))
                graph.addEdge(Edge(down, node_id, weight))

    return graph, Navigator(graph)


def build_disconnected_graph():
    graph = Graph()
    graph.addNode(Node(0, "A", 0, 0, "Waypoint"))
    graph.addNode(Node(1, "B", 10, 0, "Waypoint"))
    return graph, Navigator(graph)


def build_lazy_deletion_graph():
    graph = Graph()
    graph.addNode(Node(0, "A", 0, 0, "Waypoint"))
    graph.addNode(Node(1, "B", 10, 0, "Waypoint"))
    graph.addNode(Node(2, "C", 5, 0, "Waypoint"))
    graph.addEdge(Edge(0, 1, 10))
    graph.addEdge(Edge(0, 2, 2))
    graph.addEdge(Edge(2, 1, 3))
    return graph, Navigator(graph)


def build_early_stop_graph():
    graph = Graph()
    for i in range(6):
        graph.addNode(Node(i, f"N{i}", i, 0, "Waypoint"))
    graph.addEdge(Edge(0, 1, 1))
    graph.addEdge(Edge(1, 2, 1))
    graph.addEdge(Edge(0, 3, 1))
    graph.addEdge(Edge(3, 4, 1))
    graph.addEdge(Edge(4, 5, 1))
    return graph, Navigator(graph)


def build_equal_weight_graph():
    graph = Graph()
    graph.addNode(Node(0, "A", 0, 0, "Waypoint"))
    graph.addNode(Node(1, "B", 1, 0, "Waypoint"))
    graph.addNode(Node(2, "C", 2, 0, "Waypoint"))
    graph.addNode(Node(3, "D", 3, 0, "Waypoint"))
    graph.addEdge(Edge(0, 1, 5))
    graph.addEdge(Edge(1, 3, 5))
    graph.addEdge(Edge(0, 2, 5))
    graph.addEdge(Edge(2, 3, 5))
    return graph, Navigator(graph)


def edge_count(graph):
    return sum(len(adj) for adj in graph.adjList)
