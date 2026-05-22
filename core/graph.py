import json
import math
from pathlib import Path


class Graph:
    def __init__(self, nodes_path, edges_path):
        self.nodes_path = Path(nodes_path)
        self.edges_path = Path(edges_path)
        self.nodes = {}
        self.edges = []
        self.adjacency = {}
        self.load()

    def load(self):
        node_rows = self._read_json_list(self.nodes_path)
        edge_rows = self._read_json_list(self.edges_path)

        self.nodes = {str(node["id"]): node for node in node_rows if "id" in node}
        self.edges = edge_rows
        self.adjacency = {node_id: [] for node_id in self.nodes}

        for edge in self.edges:
            from_id, to_id = self._edge_endpoints(edge)
            if from_id not in self.nodes or to_id not in self.nodes:
                continue

            weight = self.euclidean_distance(from_id, to_id)
            self.adjacency[from_id].append((to_id, weight))

            if self._is_bidirectional(edge):
                self.adjacency[to_id].append((from_id, weight))

    def get_node_options(self):
        return [
            f"{node_id} - {node.get('name', '')}".strip()
            for node_id, node in sorted(self.nodes.items())
        ]

    def get_coordinates(self, path_ids):
        return [(self.nodes[node_id]["x"], self.nodes[node_id]["y"]) for node_id in path_ids]

    def euclidean_distance(self, from_id, to_id):
        first = self.nodes[from_id]
        second = self.nodes[to_id]
        dx = second["x"] - first["x"]
        dy = second["y"] - first["y"]
        return math.sqrt(dx * dx + dy * dy)

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
            return str(edge.get("from")), str(edge.get("to"))
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            return str(edge[0]), str(edge[1])
        return None, None

    @staticmethod
    def _is_bidirectional(edge):
        if isinstance(edge, dict):
            return bool(edge.get("bidirectional", True))
        return True
