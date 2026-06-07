import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.graph_factory import build_grid_graph, edge_count

RESULTS_PATH = Path(__file__).resolve().parent / "ket_qua_hieu_nang.csv"

CSV_COLUMNS = [
    "luoi",
    "so_dinh",
    "so_canh",
    "tu",
    "den",
    "sinh_luoi_ms",
    "warmup",
    "so_lan_do",
    "tb_dijkstra_ms",
]


def run_dijkstra(navigator, u, v):
    distances, previous = navigator.dijkstra(u, v)
    navigator.getPath(v, previous)


def measure_grid(side, runs=100, warmup=5):
    start = time.perf_counter()
    graph, navigator = build_grid_graph(side)
    build_ms = (time.perf_counter() - start) * 1000

    vertex_count = len(graph.nodes)
    edges = edge_count(graph)
    u, v = 0, vertex_count - 1

    for _ in range(warmup):
        run_dijkstra(navigator, u, v)

    total_ms = 0.0
    for _ in range(runs):
        start = time.perf_counter()
        run_dijkstra(navigator, u, v)
        total_ms += (time.perf_counter() - start) * 1000

    return {
        "side": side,
        "vertex_count": vertex_count,
        "edge_count": edges,
        "from_id": u,
        "to_id": v,
        "build_ms": build_ms,
        "warmup": warmup,
        "run_count": runs,
        "dijkstra_avg_ms": total_ms / runs,
    }


def row_to_output(row):
    return {
        "luoi": f"{row['side']}×{row['side']}",
        "so_dinh": row["vertex_count"],
        "so_canh": row["edge_count"],
        "tu": row["from_id"],
        "den": row["to_id"],
        "sinh_luoi_ms": round(row["build_ms"], 4),
        "warmup": row["warmup"],
        "so_lan_do": row["run_count"],
        "tb_dijkstra_ms": round(row["dijkstra_avg_ms"], 4),
    }


def parse_sides(value):
    sides = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        side = int(part)
        if side >= 2:
            sides.append(side)
    return sides or [10, 50, 100]


def print_table(rows):
    print("TB Dijkstra (ms) = thời gian trung bình mỗi lần dijkstra + getPath (chỉ số chính).")
    print()
    print(
        "| Lưới | Số đỉnh | Số cạnh | Sinh lưới (ms) | Warm-up | "
        "Số lần đo | >> TB Dijkstra (ms) << |"
    )
    print(
        "|------|---------|---------|----------------|---------------|"
        "----------|----------------------|"
    )
    for row in rows:
        out = row_to_output(row)
        print(
            f"| {out['luoi']} | {out['so_dinh']} | {out['so_canh']} | {out['sinh_luoi_ms']:.2f} | "
            f"{out['warmup']} | {out['so_lan_do']} | "
            f"**{out['tb_dijkstra_ms']:.4f}** |"
        )


def write_csv(rows, path):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row_to_output(row))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Đo tốc độ Dijkstra trên lưới quy mô lớn")
    parser.add_argument("--sizes", default="10,50,100", help="cạnh lưới, vd: 10,50,100,200")
    parser.add_argument("--runs", type=int, default=50, help="số lần đo Dijkstra")
    parser.add_argument("--warmup", type=int, default=5, help="số lần warm-up trước khi đo")
    args = parser.parse_args()

    rows = [measure_grid(side, runs=args.runs, warmup=args.warmup) for side in parse_sides(args.sizes)]
    print_table(rows)
    write_csv(rows, RESULTS_PATH)
    print(f"\nĐã ghi CSV: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
