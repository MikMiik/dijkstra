import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from PIL import Image, ImageTk

from core.map import CampusMap


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAP_PATH = DATA_DIR / "map.jpg"
NODES_PATH = DATA_DIR / "nodes.json"
EDGES_PATH = DATA_DIR / "edges.json"

NODE_RADIUS = 5


class NodeDialog(simpledialog.Dialog):
    def __init__(self, parent, x, y):
        self.x = x
        self.y = y
        self.result = None
        super().__init__(parent, title=f"Thêm node tại ({x}, {y})")

    def body(self, master):
        ttk.Label(master, text="Tên node").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(master, text="Loại").grid(row=1, column=0, sticky="w", padx=6, pady=4)

        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Waypoint")

        self.name_entry = ttk.Entry(master, textvariable=self.name_var, width=28)
        self.type_box = ttk.Combobox(
            master,
            textvariable=self.type_var,
            values=("Building", "Waypoint"),
            state="readonly",
            width=25,
        )

        self.name_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.type_box.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        return self.name_entry

    def validate(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Thiếu tên", "Vui lòng nhập tên node.")
            return False

        self.result = {
            "name": name,
            "x": self.x,
            "y": self.y,
            "type": self.type_var.get(),
        }
        return True


class DijkstraMapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dijkstra Map Desktop")
        self.geometry("1180x760")
        self.minsize(980, 620)

        self.mode = tk.StringVar(value="run")
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        self.distance_var = tk.StringVar(value="Tổng khoảng cách: --")
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.edge_from_var = tk.StringVar()
        self.edge_to_var = tk.StringVar()

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

        ttk.Label(toolbar, text="Chế độ").pack(side="left", padx=(0, 6))
        ttk.Radiobutton(toolbar, text="Chạy", value="run", variable=self.mode).pack(side="left")
        ttk.Radiobutton(toolbar, text="Đánh dấu", value="mark", variable=self.mode).pack(side="left", padx=(0, 14))

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
        self.canvas.bind("<Button-1>", self.handle_canvas_click)

        ttk.Label(side_frame, textvariable=self.distance_var).pack(anchor="w", pady=(0, 12))

        edge_group = ttk.LabelFrame(side_frame, text="Thêm cạnh")
        edge_group.pack(fill="x", pady=(0, 12))

        ttk.Label(edge_group, text="Đỉnh 1").pack(anchor="w", padx=8, pady=(8, 2))
        self.edge_from_box = ttk.Combobox(edge_group, textvariable=self.edge_from_var, state="readonly")
        self.edge_from_box.pack(fill="x", padx=8)

        ttk.Label(edge_group, text="Đỉnh 2").pack(anchor="w", padx=8, pady=(8, 2))
        self.edge_to_box = ttk.Combobox(edge_group, textvariable=self.edge_to_var, state="readonly")
        self.edge_to_box.pack(fill="x", padx=8)

        ttk.Button(edge_group, text="Lưu cạnh 2 chiều", command=self.add_edge).pack(fill="x", padx=8, pady=10)

        ttk.Button(side_frame, text="Tải lại dữ liệu", command=self.reload_graph).pack(fill="x")
        ttk.Label(side_frame, textvariable=self.status_var, wraplength=240).pack(anchor="w", pady=(14, 0))

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

        for combo in (self.start_box, self.end_box, self.edge_from_box, self.edge_to_box):
            combo["values"] = options

        self.redraw_map()
        self.status_var.set(f"Đã tải {len(self.graph.nodes)} node, {len(self.graph.edges)} cạnh.")

    def redraw_map(self):
        self.canvas.delete("all")
        if self.photo:
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        if not self.graph:
            return

        self._draw_edges()
        for node in self.graph.nodes.values():
            self._draw_node(node)

        self.distance_var.set("Tổng khoảng cách: --")

    def handle_canvas_click(self, event):
        if self.mode.get() != "mark":
            return

        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        dialog = NodeDialog(self, x, y)
        if not dialog.result:
            return

        nodes = self._read_json_list(NODES_PATH)
        new_id = len(nodes)
        nodes.append({"id": new_id, **dialog.result})
        self._write_json_list(NODES_PATH, nodes)
        self.reload_graph()
        self.status_var.set(f"Đã thêm node {new_id} tại ({x}, {y}).")

    def add_edge(self):
        from_id = self._selected_id(self.edge_from_var.get())
        to_id = self._selected_id(self.edge_to_var.get())

        if not from_id or not to_id:
            messagebox.showerror("Thiếu node", "Vui lòng chọn đầy đủ hai node.")
            return
        if from_id == to_id:
            messagebox.showerror("Cạnh không hợp lệ", "Hai đầu cạnh phải là hai node khác nhau.")
            return

        edges = self._read_json_list(EDGES_PATH)
        from_idx = int(from_id)
        to_idx = int(to_id)
        if any({edge.get("from"), edge.get("to")} == {from_idx, to_idx} for edge in edges if isinstance(edge, dict)):
            messagebox.showinfo("Đã tồn tại", "Cạnh này đã có trong edges.json.")
            return

        edges.append({"from": from_idx, "to": to_idx, "bidirectional": True})
        self._write_json_list(EDGES_PATH, edges)
        self.reload_graph()
        self.status_var.set(f"Đã thêm cạnh {from_id} <-> {to_id}.")

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
            if from_id not in self.graph.nodes or to_id not in self.graph.nodes:
                continue

            first = self.graph.nodes[from_id]
            second = self.graph.nodes[to_id]
            self.canvas.create_line(first["x"], first["y"], second["x"], second["y"], fill="#2f7dd1", width=2, dash=(4, 4))

    def _draw_node(self, node):
        x = node["x"]
        y = node["y"]
        color = "#1f8f4d" if node.get("type") == "Building" else "#111827"
        self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill=color, outline="white", width=2)
        self.canvas.create_text(x + 8, y - 8, text=str(node["id"]), fill="#111827", anchor="sw", font=("Segoe UI", 9, "bold"))

    @staticmethod
    def _selected_id(value):
        return value.split(" - ", 1)[0].strip() if value else ""

    @staticmethod
    def _ensure_data_files():
        DATA_DIR.mkdir(exist_ok=True)
        for path in (NODES_PATH, EDGES_PATH):
            if not path.exists() or path.stat().st_size == 0:
                path.write_text("[]\n", encoding="utf-8")

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
    def _write_json_list(path, data):
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


if __name__ == "__main__":
    app = DijkstraMapApp()
    app.mainloop()
