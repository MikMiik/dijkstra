import json
from math import inf
from pathlib import Path

from core.loader import load_graph


class CampusMap:
    def __init__(self, nodes_path, edges_path):
        self.nodes_path = Path(nodes_path)
        self.edges_path = Path(edges_path)
        self.nodes = {}
        self.edges = []
        self._graph = None
        self._navigator = None
        self.load()

    def load(self):
        edge_rows = self._read_json_list(self.edges_path)
        self._graph, self._navigator, types = load_graph(self.nodes_path, self.edges_path)
        self.edges = edge_rows
        self.nodes = {}
        for node in self._graph.nodes:
            self.nodes[node.index] = {
                "id": node.index,
                "name": node.name,
                "x": node.x,
                "y": node.y,
                "type": types.get(node.index, "Waypoint"),
            }

    def find_shortest_path(self, start_id, end_id):
        u = int(start_id)
        v = int(end_id)
        if u < 0 or u >= len(self._graph.nodes):
            raise ValueError(f"Node bắt đầu không tồn tại: {start_id}")
        if v < 0 or v >= len(self._graph.nodes):
            raise ValueError(f"Node đích không tồn tại: {end_id}")
        distances, previous = self._navigator.dijkstra(u, v)
        if distances[v] == inf:
            return [], inf
        path_idx = self._navigator.getPath(u, v, previous)
        return path_idx, distances[v]

    def get_node_options(self):
        return [
            f"{node_id} - {node.get('name', '')}".strip()
            for node_id, node in sorted(self.nodes.items())
        ]

    def get_coordinates(self, path_ids):
        return [(self.nodes[node_id]["x"], self.nodes[node_id]["y"]) for node_id in path_ids]

    @staticmethod
    def _read_json_list(path):
        if not path.exists() or path.stat().st_size == 0:
            return []
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    @staticmethod
    def _edge_endpoints(edge):
        if isinstance(edge, dict):
            return int(edge.get("from")), int(edge.get("to"))
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            return int(edge[0]), int(edge[1])
        return None, None
