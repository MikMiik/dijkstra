import sys
from math import inf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.map import CampusMap
from core.navigator import MinHeap
from tests.graph_factory import (
    build_disconnected_graph,
    build_early_stop_graph,
    build_equal_weight_graph,
    build_lazy_deletion_graph,
)

DATA_DIR = ROOT / "data"
NODES_PATH = DATA_DIR / "nodes.json"
EDGES_PATH = DATA_DIR / "edges.json"

DIST_TOLERANCE = 0.01

# Lớp A — bản đồ thật: kiểm tra tính đúng và trường hợp biên.
# Lớp B — đồ thị giả / file tạm: kiểm tra lõi thuật toán.
# TC : Test Case
# Expected : Kết quả mong đợi

EXPECTED_0_TO_25 = {"path": [0, 58, 1, 25], "dist": 220.6344497601203}
EXPECTED_SAME_NODE = {"path": [0], "dist": 0}
EXPECTED_SYMMETRIC_DIST = 220.6344497601203
EXPECTED_58_TO_1 = {"path": [58, 1], "dist": 80.22468448052632}
EXPECTED_0_TO_50 = {
    "path": [0, 58, 1, 24, 6, 35, 18, 21, 55, 47, 48, 50],
    "dist": 856.9619297263026,
}
EXPECTED_LAZY_DELETION = {"path": [0, 2, 1], "dist": 5}
EXPECTED_EARLY_STOP = {"path": [0, 1, 2], "dist": 2}
EXPECTED_EQUAL_WEIGHT_DIST = 10
VALID_EQUAL_WEIGHT_PATHS = [[0, 1, 3], [0, 2, 3]]


def format_status(passed):
    return "ĐẠT" if passed else "KHÔNG ĐẠT"


def check_path_distance(path, distance, expected_path=None, expected_dist=None, expected_len=None):
    if expected_path is not None and path != expected_path:
        return False, f"đường đi={path}"
    if expected_len is not None and len(path) != expected_len:
        return False, f"số đỉnh={len(path)}"
    if expected_dist is not None and abs(distance - expected_dist) >= DIST_TOLERANCE:
        return False, f"khoảng cách={distance}"
    return True, ""


def run_case(index, description, passed, detail=""):
    line = f"TC{index:02d} | {description} | {format_status(passed)}"
    if detail:
        line += f" | {detail}"
    print(line)
    return passed


def run_layer_a():
    campus_map = CampusMap(NODES_PATH, EDGES_PATH)
    passed_count = 0
    total = 6

    # --- Lớp A: bản đồ thật ---

    # TC01 — Đường tiêu biểu 0→25: có đường, path và khoảng cách cụ thể
    path, distance = campus_map.find_shortest_path("0", "25")
    passed, detail = check_path_distance(path, distance, EXPECTED_0_TO_25["path"], EXPECTED_0_TO_25["dist"])
    passed_count += run_case(1, "Đường tiêu biểu 0 → 25", passed, detail)

    # TC02 — Cùng điểm xuất phát và đích: khoảng cách = 0, path = [0]
    path, distance = campus_map.find_shortest_path("0", "0")
    passed, detail = check_path_distance(path, distance, EXPECTED_SAME_NODE["path"], EXPECTED_SAME_NODE["dist"])
    passed_count += run_case(2, "Cùng điểm xuất phát và đích", passed, detail)

    # TC03 — Đối xứng hai chiều: dist(0 → 25) = dist(25 → 0)
    _, dist_ab = campus_map.find_shortest_path("0", "25")
    _, dist_ba = campus_map.find_shortest_path("25", "0")
    passed = (
        abs(dist_ab - EXPECTED_SYMMETRIC_DIST) < DIST_TOLERANCE
        and abs(dist_ba - EXPECTED_SYMMETRIC_DIST) < DIST_TOLERANCE
        and abs(dist_ab - dist_ba) < DIST_TOLERANCE
    )
    passed_count += run_case(3, "Đối xứng khoảng cách 0 ↔ 25", passed, f"{dist_ab} so với {dist_ba}")

    # TC04 — Hai đỉnh kề trực tiếp: 58 → 1, khoảng cách = độ dài cạnh Euclidean
    path, distance = campus_map.find_shortest_path("58", "1")
    passed, detail = check_path_distance(path, distance, EXPECTED_58_TO_1["path"], EXPECTED_58_TO_1["dist"])
    passed_count += run_case(4, "Hai đỉnh kề 58 → 1", passed, detail)

    # TC05 — Đường tiêu biểu 0 → 50 (qua nhánh phía đông)
    path, distance = campus_map.find_shortest_path("0", "50")
    passed, detail = check_path_distance(path, distance, EXPECTED_0_TO_50["path"], EXPECTED_0_TO_50["dist"])
    passed_count += run_case(5, "Đường tiêu biểu 0 → 50", passed, detail)

    # TC06 — Đỉnh không tồn tại: 99 → 0 
    try:
        campus_map.find_shortest_path("99", "0")
        passed_count += run_case(6, "Đỉnh không tồn tại 99 → 0", False, "không phát sinh lỗi")
    except ValueError:
        passed_count += run_case(6, "Đỉnh không tồn tại 99 → 0", True)

    return passed_count, total


def run_layer_b():
    passed_count = 0
    total = 5

    # --- Lớp B: đồ thị giả / kiểm tra lõi thuật toán ---

    # TC07 — Không có đường giữa hai thành phần liên thông
    graph, navigator = build_disconnected_graph()
    distances, previous = navigator.dijkstra(0, 1)
    path = navigator.getPath(1, previous) if distances[1] != inf else []
    passed = path == [] and distances[1] == inf
    passed_count += run_case(7, "Không có đường (hai thành phần)", passed, f"đường đi={path}")

    # TC08 — Lazy deletion: nhiều bản ghi cùng đỉnh trong heap, bản cũ phải bị bỏ qua
    # A --10--> B, A --2--> C --3--> B  →  đường ngắn nhất A→B = 5 qua C, không phải 10
    graph, navigator = build_lazy_deletion_graph()
    distances, previous = navigator.dijkstra(0, 1)
    path = navigator.getPath(1, previous)
    passed, detail = check_path_distance(
        path, distances[1], EXPECTED_LAZY_DELETION["path"], EXPECTED_LAZY_DELETION["dist"]
    )
    passed_count += run_case(8, "Heap lỗi thời (lazy deletion)", passed, detail)

    # TC09 — MinHeap: pop luôn lấy phần tử có distance nhỏ nhất
    heap = MinHeap()
    heap.push(10, 1)
    heap.push(3, 2)
    heap.push(7, 0)
    pops = [heap.pop(), heap.pop(), heap.pop(), heap.pop()]
    passed = pops == [[3, 2], [7, 0], [10, 1], None]
    passed_count += run_case(9, "MinHeap pop theo thứ tự tăng dần", passed, str(pops[:3]))

    # TC10 — Early stop: gặp đích thì dừng, không cần duyệt nhánh dài phía sau
    graph, navigator = build_early_stop_graph()
    distances, previous = navigator.dijkstra(0, 2)
    path = navigator.getPath(2, previous)
    passed, detail = check_path_distance(
        path, distances[2], EXPECTED_EARLY_STOP["path"], EXPECTED_EARLY_STOP["dist"]
    )
    passed_count += run_case(10, "Dừng sớm khi gặp đích", passed, detail)

    # TC11 — Nhiều đường cùng trọng số: 0→1→3 và 0→2→3 đều = 10; chỉ cập nhật khi new_dist < distances[v]
    graph, navigator = build_equal_weight_graph()
    distances, previous = navigator.dijkstra(0, 3)
    path = navigator.getPath(3, previous)
    passed = (
        abs(distances[3] - EXPECTED_EQUAL_WEIGHT_DIST) < DIST_TOLERANCE
        and path in VALID_EQUAL_WEIGHT_PATHS
    )
    detail = f"đường đi={path}, khoảng cách={distances[3]}"
    passed_count += run_case(11, "Nhiều đường cùng trọng số", passed, detail)

    return passed_count, total


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("TC | Mô tả | Kết quả | Chi tiết")
    print("-" * 70)
    passed_a, total_a = run_layer_a()
    passed_b, total_b = run_layer_b()
    passed = passed_a + passed_b
    total = total_a + total_b
    print("-" * 70)
    print(f"Tổng: {passed}/{total} đạt")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
