# Luồng code: tìm đường `0` → `25`

Tài liệu này đi cùng code theo thứ tự thực thi thực tế — mở file nào trước, dòng nào chạy, gọi sang đâu, biến trong bộ nhớ lúc đó trông như thế nào. Bỏ qua thao tác giao diện (click, chọn combobox); chỉ mô tả luồng sau khi input đã có và ấn tìm đường ở các phần sau.

---

## 1. `main.py` — đường dẫn dữ liệu

Mở `main.py`, đọc từ trên xuống.

```11:15:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAP_PATH = DATA_DIR / "map.jpg"
NODES_PATH = DATA_DIR / "nodes.json"
EDGES_PATH = DATA_DIR / "edges.json"
```

| Biến         | Giá trị (ý nghĩa)                              |
| ------------ | ---------------------------------------------- |
| `BASE_DIR`   | Thư mục chứa `main.py` (gốc dự án `Dijkstra/`) |
| `DATA_DIR`   | `Dijkstra/data/`                               |
| `MAP_PATH`   | `Dijkstra/data/map.jpg` — ảnh nền bản đồ       |
| `NODES_PATH` | `Dijkstra/data/nodes.json` — danh sách đỉnh    |
| `EDGES_PATH` | `Dijkstra/data/edges.json` — danh sách cạnh    |

`Path(__file__).resolve().parent` lấy đường dẫn tuyệt đối tới thư mục file đang chạy, không phụ thuộc terminal đang `cd` ở đâu. Phần này chỉ chuẩn bị path; chưa đọc file.

Còn `NODE_RADIUS = 5` (dòng 17) — bán kính vẽ chấm node trên canvas; liên quan hiển thị, lướt qua.

---

## 2. Điểm vào chương trình

Bỏ qua class `NodeDialog` (dialog thêm node khi click bản đồ) và toàn bộ phần dựng UI trong `_build_ui`. Ta tìm chỗ Python thực sự bắt đầu chạy app:

```300:302:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
if __name__ == "__main__":
    app = DijkstraMapApp()
    app.mainloop()
```

- `if __name__ == "__main__"`: chỉ chạy khi gọi trực tiếp `python main.py`, không chạy khi file bị `import`.
- `app = DijkstraMapApp()`: tạo cửa sổ app; toàn bộ khởi tạo nằm trong `DijkstraMapApp.__init__` (dòng 73–93).
- `app.mainloop()`: bật vòng lặp sự kiện Tkinter — chờ click, chọn combobox, v.v. Phần thuật toán nằm trong các handler được gọi từ vòng lặp này; ta sẽ quay lại sau.

---

## 3. `DijkstraMapApp` — class chính

```72:72:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
class DijkstraMapApp(tk.Tk):
```

### 3.1. `tk.Tk` là gì?

`tkinter` (import `tk`) là thư viện GUI chuẩn của Python — vẽ cửa sổ desktop, nút, ô nhập, canvas trên hệ điều hành, không cần trình duyệt.

`tk.Tk` là **cửa sổ gốc** (root window). Một app Tkinter thường có đúng một instance `Tk`. `DijkstraMapApp` kế thừa `tk.Tk` nên bản thân app _là_ cửa sổ chính: gọi `self.title(...)`, `self.geometry(...)` trực tiếp trên `self`.

### 3.2. `__init__` — lướt phần UI, dừng ở logic khởi tạo

```73:93:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
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
```

**`super().__init__()`** — gọi constructor `tk.Tk`, tạo cửa sổ OS thật.

**Cấu hình cửa sổ (chỉ liệt kê, không đi sâu):**

| Dòng | Thuộc tính | Ý nghĩa                         |
| ---- | ---------- | ------------------------------- |
| 75   | `title`    | Tiêu đề cửa sổ                  |
| 76   | `geometry` | Kích thước ban đầu 1180×760 px  |
| 77   | `minsize`  | Kích thước tối thiểu 980×620 px |

**Biến trạng thái gắn UI (lướt qua):**

| Biến            | Kiểu        | Giá trị ban đầu          | Dùng cho                         |
| --------------- | ----------- | ------------------------ | -------------------------------- |
| `mode`          | `StringVar` | `"run"`                  | Chế độ Chạy / Đánh dấu (toolbar) |
| `status_var`    | `StringVar` | `"Sẵn sàng."`            | Dòng trạng thái dưới sidebar     |
| `distance_var`  | `StringVar` | `"Tổng khoảng cách: --"` | Hiển thị kết quả tìm đường       |
| `start_var`     | `StringVar` | rỗng                     | Combobox điểm bắt đầu            |
| `end_var`       | `StringVar` | rỗng                     | Combobox điểm đích               |
| `edge_from_var` | `StringVar` | rỗng                     | Combobox thêm cạnh — đỉnh 1      |
| `edge_to_var`   | `StringVar` | rỗng                     | Combobox thêm cạnh — đỉnh 2      |

**Biến thuật toán / dữ liệu (sẽ quay lại):**

| Biến         | Ban đầu | Sau này                                          |
| ------------ | ------- | ------------------------------------------------ |
| `self.photo` | `None`  | Ảnh bản đồ (`ImageTk.PhotoImage`)                |
| `self.graph` | `None`  | Instance `CampusMap` — lớp bọc đồ thị + Dijkstra |

**Thứ tự gọi trong `__init__`:**

1. `_ensure_data_files()` — đảm bảo thư mục và file JSON tồn tại _(mục 4)_
2. `_build_ui()` — dựng toolbar, canvas, combobox _(bỏ qua)_
3. `_load_map()` — nạp `map.jpg` lên canvas _(bỏ qua)_
4. `reload_graph()` — nạp `nodes.json`, `edges.json`, tạo `CampusMap` _(mục 5)_

---

## 4. `_ensure_data_files`

```276:280:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
    @staticmethod
    def _ensure_data_files():
        DATA_DIR.mkdir(exist_ok=True)
        for path in (NODES_PATH, EDGES_PATH):
            if not path.exists() or path.stat().st_size == 0:
                path.write_text("[]\n", encoding="utf-8")
```

**Input:** không có tham số; dùng hằng `DATA_DIR`, `NODES_PATH`, `EDGES_PATH` ở đầu file.

**Làm gì:**

1. `DATA_DIR.mkdir(exist_ok=True)` — nếu chưa có thư mục `data/` thì tạo; có rồi thì bỏ qua.
2. Vòng `for` lần lượt `nodes.json`, `edges.json`:
   - Nếu file **chưa tồn tại** hoặc **tồn tại nhưng rỗng** (`st_size == 0`):
   - Ghi nội dung `"[]\n"` — mảng JSON rỗng.

**Output / hiệu ứng:** không return; side effect là đảm bảo hai file luôn parse được thành list rỗng, tránh `FileNotFoundError` hoặc lỗi JSON khi `reload_graph()` / `_read_json_list()` chạy sau đó.

**Ghi chú:** hàm **không** tạo `map.jpg`. Thiếu ảnh bản đồ vẫn có thể chạy thuật toán; `_load_map()` (dòng 147–150) chỉ báo lỗi dialog và `return`.

---

## 5. `reload_graph`

Sau `_ensure_data_files`, `_build_ui`, `_load_map`, `__init__` gọi `reload_graph()` (dòng 93). Đây là bước **nạp đồ thị vào bộ nhớ** — từ đó `self.graph` sẵn sàng cho thuật toán.

```156:164:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
    def reload_graph(self):
        self.graph = CampusMap(NODES_PATH, EDGES_PATH)
        options = self.graph.get_node_options()

        for combo in (self.start_box, self.end_box, self.edge_from_box, self.edge_to_box):
            combo["values"] = options

        self.redraw_map()
```

**Input:** không có tham số; dùng hằng `NODES_PATH`, `EDGES_PATH`.

| Dòng    | Code                               | Thuật toán / UI                                      |
| ------- | ---------------------------------- | ---------------------------------------------------- |
| 157     | `self.graph = CampusMap(...)`      | **Đọc tiếp** — tạo object chứa `Graph` + `Navigator` |
| 158–161 | `get_node_options()`, gán combobox | UI — lướt qua                                        |
| 163     | `redraw_map()`                     | UI — lướt qua                                        |
| 164     | `status_var.set(...)`              | UI — lướt qua                                        |

`CampusMap` import từ `core.map` (dòng 8). Ta mở file đó.

---

### 5.1. `CampusMap.__init__` (`core/map.py`)

```8:16:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\map.py
class CampusMap:
    def __init__(self, nodes_path, edges_path):
        self.nodes_path = Path(nodes_path)
        self.edges_path = Path(edges_path)
        self.nodes = {}
        self.edges = []
        self._graph = None
        self._navigator = None
        self.load()
```

**Input:** `nodes_path`, `edges_path` — lúc gọi từ `reload_graph` là `NODES_PATH`, `EDGES_PATH`.

**Khởi tạo:**

| Thuộc tính                 | Ban đầu                  | Vai trò                                                                               |
| -------------------------- | ------------------------ | ------------------------------------------------------------------------------------- |
| `nodes_path`, `edges_path` | `Path` tới hai file JSON | Giữ path để đọc lại sau này                                                           |
| `nodes`                    | `{}`                     | Dict tra cứu theo **key** (`"0"`, `"25"`, …) — tọa độ, tên, loại; UI và vẽ đường dùng |
| `edges`                    | `[]`                     | List cạnh thô từ JSON — chủ yếu vẽ trên canvas                                        |
| `_graph`                   | `None`                   | Đồ thị thuật toán (`core.graph.Graph`)                                                |
| `_navigator`               | `None`                   | Bộ chạy Dijkstra (`core.navigator.Navigator`)                                         |

Cuối `__init__` gọi `self.load()` — toàn bộ nạp dữ liệu nằm ở đó.

---

### 5.2. `CampusMap.load()` (`core/map.py`)

```18:30:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\map.py
    def load(self):
        edge_rows = self._read_json_list(self.edges_path)
        self._graph, self._navigator, types = load_graph(self.nodes_path, self.edges_path)
        self.edges = edge_rows
        self.nodes = {}
        for node in self._graph.nodes:
            self.nodes[node.key] = {
                "id": node.key,
                "name": node.name,
                "x": node.x,
                "y": node.y,
                "type": types.get(node.key, "Waypoint"),
            }
```

**Dòng 19** — `edge_rows = self._read_json_list(self.edges_path)`

- Gọi: `CampusMap._read_json_list` (dòng 56–64 `map.py`), logic giống `_read_json_list` trong `main.py`.
- Input: path `edges.json`.
- Output: list dict, ví dụ `{"from": 0, "to": 1, "bidirectional": true}`. Với dữ liệu hiện tại: **66 phần tử**.

**Dòng 20** — `self._graph, self._navigator, types = load_graph(...)`

- Gọi sang `core/loader.py` — **bước xây đồ thị cho thuật toán** _(mục 5.3)_.
- Sau dòng này:
  - `self._graph` → object `Graph` (54 `Node`, danh sách kề `adjList`)
  - `self._navigator` → `Navigator`, bên trong `navigator.graph` trỏ cùng `Graph` đó
  - `types` → dict `{"0": "Building", "1": "Waypoint", ...}` lấy từ field `type` trong JSON

**Dòng 21** — `self.edges = edge_rows` — giữ bản gốc cạnh JSON (vẽ UI).

**Dòng 22–30** — Dựng `self.nodes`: duyệt `self._graph.nodes` (list theo **index**), key dict là `node.key` (ID ngoài JSON dạng chuỗi). Ví dụ sau bước này:

```python
self.nodes["0"] == {"id": "0", "name": "Cong Parabol", "x": 92, "y": 351, "type": "Building"}
self.nodes["25"] == {"id": "25", "name": "D3", "x": 585, "y": 381, "type": "Building"}
```

`load()` không return; khi `CampusMap(...)` xong, `self.graph` trong `main.py` đã có đủ dữ liệu.

---

### 5.3. `load_graph` và `resolve_vertex_index` (`core/loader.py`)

`CampusMap.load()` gọi `load_graph(self.nodes_path, self.edges_path)`. Mở `core/loader.py` — file này biến hai file JSON thành object `Graph` (danh sách kề + trọng số) và bọc thêm `Navigator`.

Trước khi đọc vòng tạo cạnh, cần hiểu `resolve_vertex_index` vì mỗi cạnh trong `edges.json` dùng **key** (`"from": 0`) trong khi thuật toán thao tác trên **index** (`0`, `1`, … vị trí trong `graph.nodes`).

---

#### 5.3.1. `resolve_vertex_index`

```9:14:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\loader.py
def resolve_vertex_index(key, graph):
    key_str = str(key)
    for i in range(len(graph.nodes)):
        if graph.nodes[i].key == key_str:
            return i
    return -1
```

**Vai trò:** map key ngoài (ID trong JSON / chuỗi user chọn) → index nội bộ dùng cho `adjList`, `Edge.from_node`, Dijkstra.

**Input:**

| Tham số | Kiểu khi gọi            | Ví dụ              |
| ------- | ----------------------- | ------------------ |
| `key`   | số hoặc chuỗi từ JSON   | `0`, `"0"`, `"25"` |
| `graph` | `Graph` đã có đủ `Node` | sau vòng tạo đỉnh  |

**Từng dòng:**

1. **`key_str = str(key)`** — chuẩn hóa về chuỗi. JSON có `"id": 0` (int), `edges.json` có `"from": 0` (int); `Node.key` luôn là `str` (dòng 5 `graph.py`: `self.key = str(key)`). Không ép `str` thì `0 == "0"` sẽ sai.
2. **`for i in range(len(graph.nodes))`** — duyệt tuần tự index `0 … 53` (54 đỉnh).
3. **`if graph.nodes[i].key == key_str`** — so khớp key, **không** giả định `index == id`. Trong dataset hiện tại id trùng thứ tự mảng (id `25` nằm ở `graph.nodes[25]`), nhưng code vẫn tra theo key để an toàn nếu JSON sắp xếp lộn xộn.
4. **`return i`** — tìm thấy → trả index.
5. **`return -1`** — hết vòng mà không khớp → “không tồn tại”. Caller xử lý khác nhau:
   - Trong `load_graph`: `continue` — bỏ cạnh lỗi, không crash.
   - Trong `find_shortest_path` (`map.py`): ném `ValueError`.

**Ví dụ cụ thể** (sau khi nạp xong 54 node):

| Gọi                                  | `key_str` | Vòng quét dừng ở                | Trả về |
| ------------------------------------ | --------- | ------------------------------- | ------ |
| `resolve_vertex_index(0, graph)`     | `"0"`     | `i=0`, `nodes[0].key == "0"`    | `0`    |
| `resolve_vertex_index("25", graph)`  | `"25"`    | `i=25`, `nodes[25].key == "25"` | `25`   |
| `resolve_vertex_index("999", graph)` | `"999"`   | duyệt hết 54 phần tử            | `-1`   |

**Độ phức tạp:** O(n) mỗi lần gọi — với 66 cạnh, tối đa ~66×54 lần so sánh; đủ cho bản đồ 54 đỉnh.

---

#### 5.3.2. `load_graph` — chữ ký và đọc file

```17:23:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\loader.py
def load_graph(nodes_path, edges_path):
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)
    with nodes_path.open("r", encoding="utf-8") as f:
        nodes_data = json.load(f)
    with edges_path.open("r", encoding="utf-8") as f:
        edges_data = json.load(f)
```

**Input:** hai path (từ `CampusMap` là `data/nodes.json`, `data/edges.json`).

**Dòng 18–19:** ép `Path` — hỗ trợ truyền string hoặc `Path`.

**Dòng 20–21:** mở `nodes.json`, `json.load` → `nodes_data`.

- Kiểu: `list[dict]`, **54 phần tử**.
- Phần tử đầu (index mảng `0`):

```json
{ "id": 0, "name": "Cong Parabol", "x": 92, "y": 351, "type": "Building" }
```

**Dòng 22–23:** tương tự → `edges_data`, **66 phần tử**. Phần tử đầu:

```json
{ "from": 0, "to": 1, "bidirectional": true }
```

Hai biến này là **dữ liệu thô**; chưa có `Graph`.

---

#### 5.3.3. Vòng tạo đỉnh

```25:32:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\loader.py
    graph = Graph()
    types = {}

    for i in range(len(nodes_data)):
        nd = nodes_data[i]
        node = Node(i, nd["id"], nd["name"], nd["x"], nd["y"])
        graph.addNode(node)
        types[str(nd["id"])] = nd.get("type", "Waypoint")
```

**Dòng 25** — `graph = Graph()`:

```python
graph.nodes == []
graph.adjList == []
```

**Dòng 26** — `types = {}` — dict phụ, không nằm trong `Graph`; `CampusMap.load()` dùng để gán `type` cho UI.

**Vòng `for i in range(len(nodes_data))`** — `i` chạy `0, 1, …, 53`. Mỗi vòng:

| Bước           | Code                                  | Kết quả với `i = 0`                                                        |
| -------------- | ------------------------------------- | -------------------------------------------------------------------------- |
| Lấy dict       | `nd = nodes_data[0]`                  | `{"id": 0, "name": "Cong Parabol", "x": 92, "y": 351, "type": "Building"}` |
| Tạo Node       | `Node(0, 0, "Cong Parabol", 92, 351)` | `index=0`, `key="0"`, `name`, `x`, `y`                                     |
| Gắn vào đồ thị | `graph.addNode(node)`                 | xem bên dưới                                                               |
| Lưu type       | `types["0"] = "Building"`             |                                                                            |

**`graph.addNode(node)`** (`graph.py` dòng 22–24):

```python
graph.nodes.append(node)      # nodes[0] = Node(...)
graph.adjList.append([])      # adjList[0] = []  — list kề rỗng, chờ cạnh
```

Sau **một** vòng (`i=0`): `len(graph.nodes)==1`, `len(graph.adjList)==1`, `adjList[0]==[]`.

Sau **hết** vòng (54 lần):

- `graph.nodes` — list 54 `Node`; truy cập `graph.nodes[i]` bằng **index** `i`.
- `graph.adjList` — list 54 list rỗng; `adjList[i]` sẽ chứa các `Edge` xuất phát từ index `i`.
- `types` — `{"0": "Building", "1": "Waypoint", …, "25": "Building", …}`.

**Phân biệt index vs key** (quan trọng cho bước sau):

|               | `index`                                      | `key`                                         |
| ------------- | -------------------------------------------- | --------------------------------------------- |
| Nguồn         | vị trí `i` trong vòng `for`                  | field `"id"` trong JSON                       |
| Kiểu          | `int`                                        | `str` (sau `Node.__init__`)                   |
| Dùng ở        | `adjList[index]`, `Edge.from_node`, Dijkstra | tra cứu user/UI, `edges.json` `"from"`/`"to"` |
| Ví dụ node D3 | `25`                                         | `"25"`                                        |

---

#### 5.3.4. Vòng tạo cạnh

```34:44:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\loader.py
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
```

Mỗi `ed` là một dict từ `edges.json`. Xét **cạnh đầu tiên** `{"from": 0, "to": 1, "bidirectional": true}`:

**Bước A — đổi key sang index**

```
u = resolve_vertex_index(0, graph)
  → key_str = "0"
  → i=0: nodes[0].key == "0"  →  u = 0

v = resolve_vertex_index(1, graph)
  → key_str = "1"
  → i=1: nodes[1].key == "1"  →  v = 1
```

Nếu `"from": 999` → `u = -1` → `continue`, cạnh không được thêm (im lặng).

**Bước B — tính trọng số**

Lấy tọa độ từ `graph.nodes[u]` và `graph.nodes[v]` (không đọc lại JSON):

- Node `0`: `(x1, y1) = (92, 351)`
- Node `1`: `(x2, y2) = (224, 352)`

```
weight = sqrt((224 - 92)² + (352 - 351)²)
       = sqrt(132² + 1²)
       = sqrt(17425)
       ≈ 132.0038
```

Trọng số = khoảng cách Euclid trên ảnh bản đồ (đơn vị pixel), không lấy từ file.

**Bước C — thêm cạnh có hướng**

`graph.addEdge(Edge(0, 1, 132.0038))` → `adjList[0].append(Edge(from_node=0, to_node=1, weight≈132.0038))`.

**Bước D — cạnh hai chiều**

`ed.get("bidirectional", True)` — nếu JSON **không** có field `bidirectional`, vẫn coi là `True`.

Thêm cạnh ngược: `graph.addEdge(Edge(1, 0, 132.0038))` → `adjList[1]` cũng có cạnh về `0`.

Sau cạnh đầu tiên, trích đoạn bộ nhớ:

```python
graph.adjList[0]  # [Edge(0→1, ~132.0038)]
graph.adjList[1]  # [Edge(1→0, ~132.0038), ... các cạnh khác sau này]
```

**`graph.addEdge`** (`graph.py` dòng 26–27): chỉ `append` vào `adjList[edge.from_node]` — không tự thêm chiều ngược; chiều ngược do vòng `if bidirectional` gọi `addEdge` lần hai.

Lặp cho 66 cạnh JSON → nhiều hơn 66 `Edge` object trong `adjList` (vì hầu hết hai chiều). Một node như index `0` có thể có nhiều neighbor trong `adjList[0]`.

---

#### 5.3.5. Giá trị trả về

```46:46:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\loader.py
    return graph, Navigator(graph), types
```

| Thành phần         | Là gì            | Trạng thái sau `return`                                            |
| ------------------ | ---------------- | ------------------------------------------------------------------ |
| `graph`            | `Graph`          | 54 node, `adjList` đầy cạnh có trọng số                            |
| `Navigator(graph)` | `Navigator`      | `navigator.graph` trỏ **cùng** object `graph`; chưa gọi `dijkstra` |
| `types`            | `dict[str, str]` | map key → `"Building"` / `"Waypoint"`                              |

`CampusMap.load()` nhận ba giá trị này ở dòng 20 `map.py`, gán `self._graph`, `self._navigator`, rồi dựng `self.nodes` dict cho UI.

**Chuỗi gọi tóm tắt:**

```text
load_graph(nodes_path, edges_path)
  → json.load × 2
  → vòng Node: Graph.nodes + Graph.adjList (list rỗng)
  → vòng Edge: resolve_vertex_index → weight → addEdge (×2 nếu bidirectional)
  → return (graph, Navigator(graph), types)
```

Gặp `Navigator(graph)` — mở `core/navigator.py` _(mục 5.3.6)_.

---

#### 5.3.6. `Navigator` và `MinHeap` (`core/navigator.py`) — ý tưởng chung

**Ý tưởng:** `Graph` giữ dữ liệu (node, cạnh, `adjList`). `Navigator` giữ **thuật toán tìm đường** chạy trên `Graph` đó — tách “bản đồ” và “cách đi trên bản đồ”. Lúc nạp graph chỉ **gắn** hai phần lại; chưa tính đường.

| Class       | Vai trò                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------ |
| `MinHeap`   | Hàng đợi ưu tiên — mỗi bước Dijkstra lấy đỉnh có khoảng cách tạm nhỏ nhất (`push` / `pop`) |
| `Navigator` | Bọc Dijkstra: nhận `Graph`, cung cấp `dijkstra` và `getPath`                               |

**Lúc `load_graph` — chỉ `Navigator.__init__`:**

|            |                                                   |
| ---------- | ------------------------------------------------- |
| **Input**  | `graph` — object `Graph` vừa xây xong             |
| **Làm gì** | `self.graph = graph` (cùng reference, không copy) |
| **Output** | Instance `Navigator` → `CampusMap._navigator`     |

Chưa gọi `dijkstra` hay `getPath`; chưa dùng `MinHeap`.

**Khi tìm đường** (`find_shortest_path`, mục 6) — `Navigator` được dùng:

| Hàm                                     | Input                                       | Làm gì                                                              | Output                                            |
| --------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------- |
| `dijkstra(start_idx, end_idx)`          | index nguồn, index đích (vd. `0`, `25`)     | Duyệt `graph.adjList` qua `MinHeap`; cập nhật khoảng cách ngắn nhất | `distances`, `previous` — hai list length 54      |
| `getPath(start_idx, end_idx, previous)` | index nguồn/đích + `previous` từ `dijkstra` | Dựng lại thứ tự index trên đường đi                                 | `path_idx` — list index, vd. `[0,1,2,3,4,5,6,25]` |

`CampusMap` đổi index → key rồi trả về UI. Chi tiết từng bước vòng lặp: mục 6.3 và 6.4.

---

### 5.4. `Graph` trong bộ nhớ sau `reload_graph`

Hai lớp dữ liệu song song trên cùng một bộ node:

|               | `CampusMap._graph` (`Graph`)         | `CampusMap.nodes` (dict)    |
| ------------- | ------------------------------------ | --------------------------- |
| Truy cập đỉnh | `graph.nodes[index]` — list          | `nodes[key]` — dict         |
| ID            | `node.index` (int), `node.key` (str) | key dict = `"0"`, `"25"`, … |
| Dùng cho      | Dijkstra, `adjList`, trọng số cạnh   | UI combobox, vẽ tọa độ      |

Ví dụ node `"0"`: `index = 0`, `key = "0"`, tọa độ `(92, 351)`. Một vài cạnh kề của index `0` nằm trong `graph.adjList[0]` — list các `Edge(from_node=0, to_node=..., weight=...)`.

Kết thúc `reload_graph`, `self.graph` trong `DijkstraMapApp` trỏ tới `CampusMap` đã nạp xong. Combobox được điền chuỗi dạng `"0 - Cong Parabol"` qua `get_node_options()` — phục vụ chọn điểm; thuật toán sẽ nhận key `"0"`, `"25"` qua `_selected_id()` khi ấn tìm đường.

---

## 6. Tìm đường `0` → `25`

**Giả định:** `reload_graph()` đã chạy; combobox đã chọn `"0 - Cong Parabol"` và `"25 - D3"`. Bỏ qua sự kiện ấn nút — coi như `find_path()` được gọi với `start_id = "0"`, `end_id = "25"`.

---

### 6.1. `find_path` (`main.py`)

```221:244:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\main.py
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
        self.status_var.set(" -> ".join(path_ids))
```

**Dòng 222–223** — Lấy ID từ combobox:

- `self.start_var.get()` → `"0 - Cong Parabol"`
- `_selected_id(...)` (dòng 272–273): tách chuỗi tại `" - "`, lấy phần đầu → `start_id = "0"`, `end_id = "25"`

**Dòng 230** — Gọi thuật toán:

```python
path_ids, distance = self.graph.find_shortest_path("0", "25")
```

`self.graph` là `CampusMap`; dòng này nhảy sang `core/map.py` _(mục 6.2)_.

**Sau khi có kết quả** (với ví dụ này):

| Dòng    | Code                         | Thuật toán / UI        |
| ------- | ---------------------------- | ---------------------- |
| 235     | `redraw_map()`               | UI — xóa vẽ cũ         |
| 241     | `get_coordinates(path_ids)`  | Đổi key → tọa độ để vẽ |
| 242     | `_draw_path(points)`         | UI — vẽ đường đỏ       |
| 243–244 | `distance_var`, `status_var` | UI — hiển thị kết quả  |

Kết quả thuật toán cho ví dụ: `path_ids = ['0','1','2','3','4','5','6','25']`, `distance = 501.63527840068963` px.

---

### 6.2. `find_shortest_path` (`core/map.py`)

```32:44:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\map.py
    def find_shortest_path(self, start_id, end_id):
        u = resolve_vertex_index(start_id, self._graph)
        v = resolve_vertex_index(end_id, self._graph)
        if u == -1:
            raise ValueError(f"Node bắt đầu không tồn tại: {start_id}")
        if v == -1:
            raise ValueError(f"Node đích không tồn tại: {end_id}")
        distances, previous = self._navigator.dijkstra(u, v)
        if distances[v] == inf:
            return [], inf
        path_idx = self._navigator.getPath(u, v, previous)
        path_ids = [self._graph.nodes[i].key for i in path_idx]
        return path_ids, distances[v]
```

**Input:** `start_id = "0"`, `end_id = "25"` (key ngoài).

| Dòng  | Gọi                                       | Input       | Output                                                     |
| ----- | ----------------------------------------- | ----------- | ---------------------------------------------------------- |
| 33    | `resolve_vertex_index("0", self._graph)`  | key         | `u = 0`                                                    |
| 34    | `resolve_vertex_index("25", self._graph)` | key         | `v = 25`                                                   |
| 39    | `self._navigator.dijkstra(0, 25)`         | index       | `distances`, `previous` _(mục 6.3)_                        |
| 40–41 | `distances[25] == inf?`                   |             | `False` — có đường đi                                      |
| 42    | `getPath(0, 25, previous)`                |             | `path_idx = [0,1,2,3,4,5,6,25]` _(mục 6.4)_                |
| 43    | list comprehension                        | index → key | `path_ids = ['0','1','2','3','4','5','6','25']`            |
| 44    | `return`                                  |             | `(['0','1','2','3','4','5','6','25'], 501.63527840068963)` |

Từ đây trở đi mọi thao tác trên đồ thị dùng **index**, không dùng key — `Navigator` chỉ làm việc với `Graph.adjList`.

---

### 6.3. `Navigator.dijkstra(0, 25)` (`core/navigator.py`)

```37:59:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\navigator.py
    def dijkstra(self, start_idx, end_idx):
        n = len(self.graph.nodes)
        distances = [float("inf")] * n
        previous = [-1] * n
        distances[start_idx] = 0
        pq = MinHeap()
        pq.push(0, start_idx)
        while len(pq.heap) > 0:
            current_item = pq.pop()
            current_dist = current_item[0]
            u = current_item[1]
            if u == end_idx:
                break
            if current_dist > distances[u]:
                continue
            for edge in self.graph.getNeighbors(u):
                v = edge.to_node
                new_dist = current_dist + edge.weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    previous[v] = u
                    pq.push(new_dist, v)
        return distances, previous
```

**Mục tiêu:** từ index `0`, tìm đường rẻ nhất tới index `25` trên `Graph` (tổng trọng số cạnh nhỏ nhất).

**Khởi tạo (dòng 38–43):**

- `n = 54`
- `distances` — list 54 phần tử, ban đầu toàn `inf`; sau dòng 41: `distances[0] = 0`
- `previous` — list 54 phần tử, ban đầu toàn `-1`
- `pq.push(0, 0)` → heap: `[[0, 0]]`

**Trace đầy đủ vòng `while`** (`start_idx=0`, `end_idx=25`). Mỗi bước = một lần `pq.pop()`. Cạnh ghi dạng `u→v` theo **index**; `w` = trọng số cạnh trong `adjList`.

- **relax** — `new_dist < distances[v]`: cập nhật khoảng cách nhỏ hơn, gán `previous`, push heap.
- **skip** — duyệt cạnh nhưng `new_dist >= distances[v]`: không đổi gì.
- **stale** — bản ghi cũ trong heap: `current_dist > distances[u]`, `continue` không relax.

**Bước 1** — `pop (0.0000, 0)` key `"0"`

- `u != 25`, không stale
- relax `0→1` w=132.0038: `distances[1]` inf → 132.0038, `previous[1]=0`, push `(132.0038, 1)`

**Bước 2** — `pop (132.0038, 1)` key `"1"`

- skip `1→0` w=132.0038 (new=264.0076 ≥ dist[0]=0)
- relax `1→2` w=30.0000: `distances[2]` inf → 162.0038, `previous[2]=1`, push `(162.0038, 2)`
- relax `1→47` w=70.0071: `distances[47]` inf → 202.0109, `previous[47]=1`, push `(202.0109, 47)`

**Bước 3** — `pop (162.0038, 2)` key `"2"`

- skip `2→1` w=30.0000 (new=192.0038 ≥ dist[1]=132.0038)
- relax `2→3` w=71.0282: `distances[3]` inf → 233.0320, `previous[3]=2`, push `(233.0320, 3)`
- relax `2→45` w=114.6909: `distances[45]` inf → 276.6947, `previous[45]=2`, push `(276.6947, 45)`

**Bước 4** — `pop (202.0109, 47)` key `"47"`

- relax `47→18` w=28.0179: `distances[18]` inf → 230.0288, `previous[18]=47`, push `(230.0288, 18)`
- skip `47→1` w=70.0071 (new=272.0181 ≥ dist[1]=132.0038)
- relax `47→20` w=58.0000: `distances[20]` inf → 260.0109, `previous[20]=47`, push `(260.0109, 20)`

**Bước 5** — `pop (230.0288, 18)` key `"18"`

- skip `18→47` w=28.0179 (new=258.0466 ≥ dist[47]=202.0109)

**Bước 6** — `pop (233.0320, 3)` key `"3"`

- skip `3→2` w=71.0282 (new=304.0601 ≥ dist[2]=162.0038)
- relax `3→4` w=67.1863: `distances[4]` inf → 300.2183, `previous[4]=3`, push `(300.2183, 4)`

**Bước 7** — `pop (260.0109, 20)` key `"20"`

- relax `20→19` w=50.3587: `distances[19]` inf → 310.3696, `previous[19]=20`, push `(310.3696, 19)`
- relax `20→21` w=57.4282: `distances[21]` inf → 317.4391, `previous[21]=20`, push `(317.4391, 21)`
- relax `20→22` w=61.0328: `distances[22]` inf → 321.0437, `previous[22]=20`, push `(321.0437, 22)`
- skip `20→47` w=58.0000 (new=318.0109 ≥ dist[47]=202.0109)

**Bước 8** — `pop (276.6947, 45)` key `"45"`

- skip `45→2` w=114.6909 (new=391.3856 ≥ dist[2]=162.0038)
- skip `45→4` w=102.2008 (new=378.8955 ≥ dist[4]=300.2183)
- relax `45→8` w=88.4590: `distances[8]` inf → 365.1537, `previous[8]=45`, push `(365.1537, 8)`
- relax `45→15` w=90.2552: `distances[15]` inf → 366.9499, `previous[15]=45`, push `(366.9499, 15)`
- relax `45→17` w=67.0000: `distances[17]` inf → 343.6947, `previous[17]=45`, push `(343.6947, 17)`

**Bước 9** — `pop (300.2183, 4)` key `"4"`

- skip `4→3` w=67.1863 (new=367.4046 ≥ dist[3]=233.0320)
- relax `4→5` w=22.0227: `distances[5]` inf → 322.2410, `previous[5]=4`, push `(322.2410, 5)`
- skip `4→45` w=102.2008 (new=402.4190 ≥ dist[45]=276.6947)

**Bước 10** — `pop (310.3696, 19)` key `"19"`

- skip `19→20` w=50.3587 (new=360.7284 ≥ dist[20]=260.0109)

**Bước 11** — `pop (317.4391, 21)` key `"21"`

- skip `21→20` w=57.4282 (new=374.8674 ≥ dist[20]=260.0109)
- skip `21→22` w=26.0192 (new=343.4584 ≥ dist[22]=321.0437)
- relax `21→53` w=44.9222: `distances[53]` inf → 362.3613, `previous[53]=21`, push `(362.3613, 53)`

**Bước 12** — `pop (321.0437, 22)` key `"22"`

- skip `22→20` w=61.0328 (new=382.0765 ≥ dist[20]=260.0109)
- skip `22→21` w=26.0192 (new=347.0629 ≥ dist[21]=317.4391)
- skip `22→53` w=43.9659 (new=365.0096 ≥ dist[53]=362.3613)

**Bước 13** — `pop (322.2410, 5)` key `"5"`

- skip `5→4` w=22.0227 (new=344.2637 ≥ dist[4]=300.2183)
- relax `5→6` w=125.0160: `distances[6]` inf → 447.2570, `previous[6]=5`, push `(447.2570, 6)`
- relax `5→23` w=100.6876: `distances[23]` inf → 422.9286, `previous[23]=5`, push `(422.9286, 23)`

**Bước 14** — `pop (343.6947, 17)` key `"17"`

- skip `17→45` w=67.0000 (new=410.6947 ≥ dist[45]=276.6947)
- relax `17→9` w=85.7263: `distances[9]` inf → 429.4210, `previous[9]=17`, push `(429.4210, 9)`
- relax `17→11` w=104.1729: `distances[11]` inf → 447.8676, `previous[11]=17`, push `(447.8676, 11)`
- relax `17→14` w=89.0225: `distances[14]` inf → 432.7171, `previous[14]=17`, push `(432.7171, 14)`

**Bước 15** — `pop (362.3613, 53)` key `"53"`

- skip `53→21` w=44.9222 (new=407.2835 ≥ dist[21]=317.4391)
- skip `53→22` w=43.9659 (new=406.3272 ≥ dist[22]=321.0437)
- relax `53→46` w=45.0999: `distances[46]` inf → 407.4612, `previous[46]=53`, push `(407.4612, 46)`

**Bước 16** — `pop (365.1537, 8)` key `"8"`

- skip `8→45` w=88.4590 (new=453.6127 ≥ dist[45]=276.6947)
- skip `8→9` w=76.1643 (new=441.3180 ≥ dist[9]=429.4210)

**Bước 17** — `pop (366.9499, 15)` key `"15"`

- relax `15→14` w=54.0000: `distances[14]` 432.7171 → 420.9499, `previous[14]=15`, push `(420.9499, 14)`
- relax `15→16` w=40.0500: `distances[16]` inf → 406.9998, `previous[16]=15`, push `(406.9998, 16)`
- skip `15→45` w=90.2552 (new=457.2051 ≥ dist[45]=276.6947)

**Bước 18** — `pop (406.9998, 16)` key `"16"`

- skip `16→15` w=40.0500 (new=447.0498 ≥ dist[15]=366.9499)

**Bước 19** — `pop (407.4612, 46)` key `"46"`

- skip `46→23` w=112.6987 (new=520.1599 ≥ dist[23]=422.9286)
- relax `46→24` w=110.6797: `distances[24]` inf → 518.1409, `previous[24]=46`, push `(518.1409, 24)`
- skip `46→53` w=45.0999 (new=452.5611 ≥ dist[53]=362.3613)

**Bước 20** — `pop (420.9499, 14)` key `"14"`

- relax `14→13` w=54.0000: `distances[13]` inf → 474.9499, `previous[13]=14`, push `(474.9499, 13)`
- skip `14→15` w=54.0000 (new=474.9499 ≥ dist[15]=366.9499)
- skip `14→17` w=89.0225 (new=509.9723 ≥ dist[17]=343.6947)

**Bước 21** — `pop (422.9286, 23)` key `"23"`

- skip `23→5` w=100.6876 (new=523.6162 ≥ dist[5]=322.2410)
- skip `23→6` w=105.7592 (new=528.6878 ≥ dist[6]=447.2570)
- skip `23→46` w=112.6987 (new=535.6273 ≥ dist[46]=407.4612)

**Bước 22** — `pop (429.4210, 9)` key `"9"`

- skip `9→8` w=76.1643 (new=505.5853 ≥ dist[8]=365.1537)
- relax `9→10` w=78.0064: `distances[10]` inf → 507.4274, `previous[10]=9`, push `(507.4274, 10)`
- skip `9→17` w=85.7263 (new=515.1473 ≥ dist[17]=343.6947)

**Bước 23** — `pop (432.7171, 14)` key `"14"`

- stale: `current_dist=432.7171 > distances[14]=420.9499` → `continue` (dòng 50–51), không relax

**Bước 24** — `pop (447.2570, 6)` key `"6"`

- skip `6→5` w=125.0160 (new=572.2730 ≥ dist[5]=322.2410)
- relax `6→7` w=121.0000: `distances[7]` inf → 568.2570, `previous[7]=6`, push `(568.2570, 7)`
- skip `6→23` w=105.7592 (new=553.0161 ≥ dist[23]=422.9286)
- relax `6→49` w=88.0909: `distances[49]` inf → 535.3478, `previous[49]=6`, push `(535.3478, 49)`
- relax `6→30` w=79.6304: `distances[30]` inf → 526.8874, `previous[30]=6`, push `(526.8874, 30)`
- relax `6→25` w=54.3783: `distances[25]` inf → **501.6353**, `previous[25]=6`, push `(501.6353, 25)`
- relax `6→51` w=134.3726: `distances[51]` inf → 581.6296, `previous[51]=6`, push `(581.6296, 51)`

**Bước 25** — `pop (447.8676, 11)` key `"11"`

- skip `11→10` w=89.0056 (new=536.8732 ≥ dist[10]=507.4274)
- relax `11→12` w=82.0061: `distances[12]` inf → 529.8737, `previous[12]=11`, push `(529.8737, 12)`
- skip `11→17` w=104.1729 (new=552.0405 ≥ dist[17]=343.6947)

**Bước 26** — `pop (474.9499, 13)` key `"13"`

- relax `13→12` w=47.0106: `distances[12]` 529.8737 → 521.9605, `previous[12]=13`, push `(521.9605, 12)`
- skip `13→14` w=54.0000 (new=528.9499 ≥ dist[14]=420.9499)

**Bước 27** — `pop (501.6353, 25)` key `"25"`

- `u == end_idx` → **`break`** (dòng 48–49). Vòng `while` kết thúc.

**`return distances, previous` (dòng 59):**

- `distances[25] = 501.63527840068963`
- Chuỗi `previous` trên đường tối ưu: `previous[25]=6`, `previous[6]=5`, `previous[5]=4`, `previous[4]=3`, `previous[3]=2`, `previous[2]=1`, `previous[1]=0`, `previous[0]=-1`

Tổng cộng **27 lần pop**; thuật toán dừng sớm khi pop ra index `25`, không duyệt hết 54 đỉnh.

---

### 6.4. `Navigator.getPath(0, 25, previous)`

```61:70:d:\ĐHBK\2025.2\CTDL>\CK\Dijkstra\core\navigator.py
    def getPath(self, start_idx, end_idx, previous):
        path = []
        current = end_idx
        while current != -1:
            path.append(current)
            current = previous[current]
        n = len(path)
        for i in range(n // 2):
            path[i], path[n - i - 1] = path[n - i - 1], path[i]
        return path
```

Dijkstra đã tính **ngược** (từ nguồn lan ra); `getPath` **dựng lại** danh sách index từ đích về nguồn rồi đảo:

| Vòng | `current` | `previous[current]` | `path` sau append                        |
| ---- | --------- | ------------------- | ---------------------------------------- |
| 1    | 25        | 6                   | `[25]`                                   |
| 2    | 6         | 5                   | `[25, 6]`                                |
| 3    | 5         | 4                   | `[25, 6, 5]`                             |
| 4    | 4         | 3                   | `[25, 6, 5, 4]`                          |
| 5    | 3         | 2                   | `[25, 6, 5, 4, 3]`                       |
| 6    | 2         | 1                   | `[25, 6, 5, 4, 3, 2]`                    |
| 7    | 1         | 0                   | `[25, 6, 5, 4, 3, 2, 1]`                 |
| 8    | 0         | -1                  | `[25, 6, 5, 4, 3, 2, 1, 0]` → thoát vòng |

Đảo mảng → **`[0, 1, 2, 3, 4, 5, 6, 25]`** — đúng thứ tự đi từ start tới end.

`find_shortest_path` dòng 43 đổi sang key: `['0','1','2','3','4','5','6','25']`.

---

### 6.5. Trả về `find_path` — tóm tắt luồng

```text
find_path()
  start_id="0", end_id="25"
  → CampusMap.find_shortest_path("0", "25")
      u=0, v=25
      → Navigator.dijkstra(0, 25)     → distances, previous
      → Navigator.getPath(0, 25, previous)  → [0, 1, 2, 3, 4, 5, 6, 25]
      → đổi index → key
  ← path_ids=['0','1','2','3','4','5','6','25'], distance=501.63527840068963
  → get_coordinates → vẽ (UI)
```

Đường đi đi theo chuỗi cạnh liên tiếp `0—1—2—3—4—5—6` rồi nhánh `6—25` — khớp với cạnh trong `edges.json`, không phải đường chim bay thẳng trên bản đồ.

---

_(Hết luồng tìm đường `0` → `25`.)_
