import heapq
from math import inf


def shortest_path(adjacency, start_id, end_id):
    """Return (path_ids, total_distance) using Dijkstra with a min-heap."""
    if start_id not in adjacency:
        raise ValueError(f"Node bắt đầu không tồn tại: {start_id}")
    if end_id not in adjacency:
        raise ValueError(f"Node đích không tồn tại: {end_id}")

    distances = {node_id: inf for node_id in adjacency}
    previous = {node_id: None for node_id in adjacency}
    distances[start_id] = 0.0

    heap = [(0.0, start_id)]
    visited = set()

    while heap:
        current_distance, current_id = heapq.heappop(heap)
        if current_id in visited:
            continue

        visited.add(current_id)
        if current_id == end_id:
            break

        for neighbor_id, weight in adjacency[current_id]:
            if neighbor_id in visited:
                continue

            candidate = current_distance + weight
            if candidate < distances[neighbor_id]:
                distances[neighbor_id] = candidate
                previous[neighbor_id] = current_id
                heapq.heappush(heap, (candidate, neighbor_id))

    if distances[end_id] == inf:
        return [], inf

    path = []
    node_id = end_id
    while node_id is not None:
        path.append(node_id)
        node_id = previous[node_id]

    path.reverse()
    return path, distances[end_id]
