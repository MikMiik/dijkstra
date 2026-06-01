import json
from math import inf
from pathlib import Path

from core.loader import load_graph, resolve_vertex_index


class Graph:
    def __init__(self, nodes_path, edges_path):
        self.nodes_path = Path(nodes_path)
        self.edges_path = Path(edges_path)
        self.nodes = {}
        self.edges = []
        self._td_graph = None
        self._navigator = None
        self.load()

    def load(self):
        edge_rows = self._read_json_list(self.edges_path)
        self._td_graph, self._navigator, types = load_graph(self.nodes_path, self.edges_path)
        self.edges = edge_rows
        self.nodes = {}
        for node in self._td_graph.nodes:
            self.nodes[node.key] = {
                "id": node.key,
                "name": node.name,
                "x": node.x,
                "y": node.y,
                "type": types.get(node.key, "Waypoint"),
            }

    def find_shortest_path(self, start_id, end_id):
        u = resolve_vertex_index(start_id, self._td_graph)
        v = resolve_vertex_index(end_id, self._td_graph)
        if u == -1:
            raise ValueError(f"Node bắt đầu không tồn tại: {start_id}")
        if v == -1:
            raise ValueError(f"Node đích không tồn tại: {end_id}")
        distances, previous = self._navigator.dijkstra(u, v)
        if distances[v] == inf:
            return [], inf
        path_idx = self._navigator.getPath(u, v, previous)
        path_ids = [self._td_graph.nodes[i].key for i in path_idx]
        return path_ids, distances[v]

    def get_node_options(self):
        return [
            f"{node_id} - {node.get('name', '')}".strip()
            for node_id, node in sorted(self.nodes.items(), key=lambda item: int(item[0]) if item[0].isdigit() else item[0])
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
            return str(edge.get("from")), str(edge.get("to"))
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            return str(edge[0]), str(edge[1])
        return None, None
