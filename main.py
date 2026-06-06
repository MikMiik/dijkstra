import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from core.map import CampusMap


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAP_PATH = DATA_DIR / "map.jpg"
NODES_PATH = DATA_DIR / "nodes.json"
EDGES_PATH = DATA_DIR / "edges.json"

NODE_RADIUS = 5


class DijkstraMapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dijkstra Map Desktop")
        self.geometry("1180x760")
        self.minsize(980, 620)

        self.status_var = tk.StringVar(value="Sẵn sàng.")
        self.distance_var = tk.StringVar(value="Tổng khoảng cách: --")
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        self.photo = None
        self.graph = None

        self._ensure_data_files()
        self._build_ui()
        self._load_map()
        self.reload_graph()

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Label(toolbar, text="Tu").pack(side="left")
        self.start_box = ttk.Combobox(toolbar, textvariable=self.start_var, width=28, state="readonly")
        self.start_box.pack(side="left", padx=6)

        ttk.Label(toolbar, text="Den").pack(side="left")
        self.end_box = ttk.Combobox(toolbar, textvariable=self.end_var, width=28, state="readonly")
        self.end_box.pack(side="left", padx=6)

        ttk.Button(toolbar, text="Tìm đường", command=self.find_path).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Xóa vẽ", command=self.redraw_map).pack(side="left", padx=6)

        content = ttk.PanedWindow(root, orient="horizontal")
        content.pack(fill="both", expand=True)

        canvas_frame = ttk.Frame(content)
        side_frame = ttk.Frame(content, width=260)
        content.add(canvas_frame, weight=4)
        content.add(side_frame, weight=1)

        self.canvas = tk.Canvas(canvas_frame, background="#f4f4f4", highlightthickness=1, highlightbackground="#c8c8c8")
        self.canvas.pack(fill="both", expand=True)

        ttk.Label(side_frame, textvariable=self.distance_var).pack(anchor="w", pady=(0, 12))
        ttk.Label(side_frame, textvariable=self.status_var, wraplength=240).pack(anchor="w")

    def _load_map(self):
        if not MAP_PATH.exists():
            messagebox.showerror("Thiếu bản đồ", f"Không tìm thấy file: {MAP_PATH}")
            return

        image = Image.open(MAP_PATH)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.config(width=image.width, height=image.height, scrollregion=(0, 0, image.width, image.height))

    def reload_graph(self):
        self.graph = CampusMap(NODES_PATH, EDGES_PATH)
        options = self.graph.get_node_options()

        for combo in (self.start_box, self.end_box):
            combo["values"] = options

        self.redraw_map()

    def redraw_map(self):
        self.canvas.delete("all")
        if self.photo:
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        if not self.graph:
            return

        self._draw_edges()
        for node in self.graph.nodes:
            self._draw_node(node)

        self.distance_var.set("Tổng khoảng cách: --")

    def find_path(self):
        start_id = self._selected_id(self.start_var.get())
        end_id = self._selected_id(self.end_var.get())

        if not start_id or not end_id:
            messagebox.showerror("Thiếu điểm", "Vui lòng chọn node bắt đầu và node đích.")
            return

        try:
            path_ids, distance = self.graph.find_shortest_path(start_id, end_id)
        except ValueError as exc:
            messagebox.showerror("Lỗi dữ liệu", str(exc))
            return

        self.redraw_map()
        if not path_ids:
            self.distance_var.set("Không tìm thấy đường đi.")
            self.status_var.set(f"Không có đường từ {start_id} đến {end_id}.")
            return

        points = self.graph.get_coordinates(path_ids)
        self._draw_path(points)
        self.distance_var.set(f"Tổng khoảng cách: {distance:.2f} px")
        self.status_var.set(" -> ".join(str(node_id) for node_id in path_ids))

    def _draw_path(self, points):
        if len(points) >= 2:
            flattened = [value for point in points for value in point]
            self.canvas.create_line(*flattened, fill="#ff2d20", width=5, capstyle="round", joinstyle="round")

        for x, y in points:
            self.canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#ffcc00", outline="#6d3b00", width=2)

    def _draw_edges(self):
        for edge in self.graph.edges:
            from_id, to_id = self.graph._edge_endpoints(edge)
            if from_id < 0 or to_id < 0 or from_id >= len(self.graph.nodes) or to_id >= len(self.graph.nodes):
                continue

            first = self.graph.nodes[from_id]
            second = self.graph.nodes[to_id]
            self.canvas.create_line(first.x, first.y, second.x, second.y, fill="#2f7dd1", width=2, dash=(4, 4))

    def _draw_node(self, node):
        x = node.x
        y = node.y
        color = "#1f8f4d" if node.type == "Building" else "#111827"
        self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill=color, outline="white", width=2)
        self.canvas.create_text(x + 8, y - 8, text=str(node.id), fill="#111827", anchor="sw", font=("Segoe UI", 9, "bold"))

    @staticmethod
    def _selected_id(value):
        return value.split(" - ", 1)[0].strip() if value else ""

    @staticmethod
    def _ensure_data_files():
        DATA_DIR.mkdir(exist_ok=True)
        for path in (NODES_PATH, EDGES_PATH):
            if not path.exists() or path.stat().st_size == 0:
                path.write_text("[]\n", encoding="utf-8")


if __name__ == "__main__":
    app = DijkstraMapApp()
    app.mainloop()
