# Luồng code: tìm đường `0` → `25`

Tài liệu này đi cùng code theo thứ tự thực thi thực tế — mở file nào trước, dòng nào chạy, gọi sang đâu, biến trong bộ nhớ lúc đó trông như thế nào. Bỏ qua thao tác giao diện (click, chọn combobox); chỉ mô tả luồng sau khi input đã có và ấn tìm đường ở các phần sau.

---

## 1. `main.py` — đường dẫn dữ liệu

Mở `main.py`, đọc từ trên xuống.

```10:14:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
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

Bỏ qua toàn bộ phần dựng UI trong `_build_ui`. Ta tìm chỗ Python thực sự bắt đầu chạy app:

```165:167:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
if __name__ == "__main__":
    app = DijkstraMapApp()
    app.mainloop()
```

- `if __name__ == "__main__"`: chỉ chạy khi gọi trực tiếp `python main.py`, không chạy khi file bị `import`.
- `app = DijkstraMapApp()`: tạo cửa sổ app; toàn bộ khởi tạo nằm trong `DijkstraMapApp.__init__` (dòng 20–37).
- `app.mainloop()`: bật vòng lặp sự kiện Tkinter — chờ click, chọn combobox, v.v. Phần thuật toán nằm trong các handler được gọi từ vòng lặp này; ta sẽ quay lại sau.

---

## 3. `DijkstraMapApp` — class chính

```19:19:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
class DijkstraMapApp(tk.Tk):
```

### 3.1. `tk.Tk` là gì?

`tkinter` (import `tk`) là thư viện GUI chuẩn của Python — vẽ cửa sổ desktop, nút, ô nhập, canvas trên hệ điều hành, không cần trình duyệt.

`tk.Tk` là **cửa sổ gốc** (root window). Một app Tkinter thường có đúng một instance `Tk`. `DijkstraMapApp` kế thừa `tk.Tk` nên bản thân app _là_ cửa sổ chính: gọi `self.title(...)`, `self.geometry(...)` trực tiếp trên `self`.

### 3.2. `__init__` — lướt phần UI, dừng ở logic khởi tạo

```20:37:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
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
```

**`super().__init__()`** — gọi constructor `tk.Tk`, tạo cửa sổ OS thật.

**Cấu hình cửa sổ (chỉ liệt kê, không đi sâu):**

| Dòng | Thuộc tính | Ý nghĩa                         |
| ---- | ---------- | ------------------------------- |
| 22   | `title`    | Tiêu đề cửa sổ                  |
| 23   | `geometry` | Kích thước ban đầu 1180×760 px  |
| 24   | `minsize`  | Kích thước tối thiểu 980×620 px |

**Biến trạng thái gắn UI (lướt qua):**

| Biến           | Kiểu        | Giá trị ban đầu          | Dùng cho                   |
| -------------- | ----------- | ------------------------ | -------------------------- |
| `status_var`   | `StringVar` | `"Sẵn sàng."`            | Dòng trạng thái dưới sidebar |
| `distance_var` | `StringVar` | `"Tổng khoảng cách: --"` | Hiển thị kết quả tìm đường |
| `start_var`    | `StringVar` | rỗng                     | Combobox điểm bắt đầu      |
| `end_var`      | `StringVar` | rỗng                     | Combobox điểm đích         |

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

```157:162:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
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

**Ghi chú:** hàm **không** tạo `map.jpg`. Thiếu ảnh bản đồ vẫn có thể chạy thuật toán; `_load_map()` (dòng 71–74) chỉ báo lỗi dialog và `return`.

---

## 5. `reload_graph`

Sau `_ensure_data_files`, `_build_ui`, `_load_map`, `__init__` gọi `reload_graph()` (dòng 37). Đây là bước **nạp đồ thị vào bộ nhớ** — từ đó `self.graph` sẵn sàng cho thuật toán.

```80:87:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
    def reload_graph(self):
        self.graph = CampusMap(NODES_PATH, EDGES_PATH)
        options = self.graph.get_node_options()

        for combo in (self.start_box, self.end_box):
            combo["values"] = options

        self.redraw_map()
```

**Input:** không có tham số; dùng hằng `NODES_PATH`, `EDGES_PATH`.

| Dòng    | Code                               | Thuật toán / UI                                      |
| ------- | ---------------------------------- | ---------------------------------------------------- |
| 81      | `self.graph = CampusMap(...)`      | **Đọc tiếp** — tạo object chứa `Graph` + `Navigator` |
| 82–85   | `get_node_options()`, gán combobox | UI — lướt qua                                        |
| 87      | `redraw_map()`                     | UI — lướt qua                                        |

`CampusMap` import từ `core.map` (dòng 8). Ta mở file đó.

---

### 5.1. `CampusMap.__init__` (`core/map.py`)

```8:15:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\map.py
class CampusMap:
    def __init__(self, nodes_path, edges_path):
        self.nodes_path = Path(nodes_path)
        self.edges_path = Path(edges_path)
        self.edges = []
        self._graph = None
        self._navigator = None
        self.load()
```

**Input:** `nodes_path`, `edges_path` — lúc gọi từ `reload_graph` là `NODES_PATH`, `EDGES_PATH`.

**Khởi tạo:**

| Thuộc tính                 | Ban đầu                  | Vai trò                                                        |
| -------------------------- | ------------------------ | -------------------------------------------------------------- |
| `nodes_path`, `edges_path` | `Path` tới hai file JSON | Giữ path để đọc lại sau này                                    |
| `edges`                    | `[]`                     | List cạnh thô từ JSON — chủ yếu vẽ trên canvas                 |
| `_graph`                   | `None`                   | Đồ thị thuật toán (`core.graph.Graph`)                         |
| `_navigator`               | `None`                   | Bộ chạy Dijkstra (`core.navigator.Navigator`)                  |

Danh sách node không lưu riêng — truy cập qua property `nodes` (trả về `self._graph.nodes`).

Cuối `__init__` gọi `self.load()` — toàn bộ nạp dữ liệu nằm ở đó.

---

### 5.2. `CampusMap.load()` (`core/map.py`)

```17:19:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\map.py
    def load(self):
        self.edges = self._read_json_list(self.edges_path)
        self._graph, self._navigator = loadData(self.nodes_path, self.edges_path)
```

**Dòng 18** — `self.edges = self._read_json_list(self.edges_path)`

- Gọi: `CampusMap._read_json_list` (dòng 40–49 `map.py`).
- Input: path `edges.json`.
- Output: list dict, ví dụ `{"from": 0, "to": 1, "bidirectional": true}`. Với dữ liệu hiện tại: **66 phần tử**.
- Giữ bản gốc cạnh JSON để vẽ trên canvas (`_draw_edges`).

**Dòng 19** — `self._graph, self._navigator = loadData(...)`

- Gọi sang `core/loader.py` — **bước xây đồ thị cho thuật toán** _(mục 5.3)_.
- Sau dòng này:
  - `self._graph` → object `Graph` (54 `Node`, danh sách kề `adjList`)
  - `self._navigator` → `Navigator`, bên trong `navigator.graph` trỏ cùng `Graph` đó

Mỗi `Node` đã mang sẵn `id`, `name`, `x`, `y`, `type` — không cần dict phụ. Ví dụ:

```python
self._graph.nodes[0].id   == 0
self._graph.nodes[0].name == "Cong Parabol"
self._graph.nodes[0].type == "Building"
self._graph.nodes[25].name == "D3"
```

`load()` không return; khi `CampusMap(...)` xong, `self.graph` trong `main.py` đã có đủ dữ liệu.

---

### 5.3. `loadData` (`core/loader.py`)

`CampusMap.load()` gọi `loadData(self.nodes_path, self.edges_path)`. Mở `core/loader.py` — file này biến hai file JSON thành object `Graph` (danh sách kề + trọng số) và bọc thêm `Navigator`.

**Định danh thống nhất:** `id` trong JSON, `Node.id`, vị trí trong `graph.nodes`, và `from`/`to` trong `edges.json` đều là **cùng một số nguyên** (`0`, `1`, …, `53`). Không còn tách `index` vs `key`, không cần hàm tra cứu trung gian.

---

#### 5.3.1. `loadData` — chữ ký và đọc file

```9:15:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\loader.py
def loadData(nodes_path, edges_path):
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)
    with nodes_path.open("r", encoding="utf-8") as f:
        nodes_data = json.load(f)
    with edges_path.open("r", encoding="utf-8") as f:
        edges_data = json.load(f)
```

**Input:** hai path (từ `CampusMap` là `data/nodes.json`, `data/edges.json`).

**Dòng 10–11:** ép `Path` — hỗ trợ truyền string hoặc `Path`.

**Dòng 12–13:** mở `nodes.json`, `json.load` → `nodes_data`.

- Kiểu: `list[dict]`, **54 phần tử**.
- Phần tử đầu (index mảng `0`):

```json
{ "id": 0, "name": "Cong Parabol", "x": 92, "y": 351, "type": "Building" }
```

**Dòng 14–15:** tương tự → `edges_data`, **66 phần tử**. Phần tử đầu:

```json
{ "from": 0, "to": 1, "bidirectional": true }
```

Hai biến này là **dữ liệu thô**; chưa có `Graph`.

---

#### 5.3.2. Vòng tạo đỉnh

```17:21:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\loader.py
    graph = Graph()

    for i in range(len(nodes_data)):
        nd = nodes_data[i]
        graph.addNode(Node(i, nd["name"], nd["x"], nd["y"], nd["type"]))
```

**Dòng 17** — `graph = Graph()`:

```python
graph.nodes == []
graph.adjList == []
```

**Vòng `for i in range(len(nodes_data))`** — `i` chạy `0, 1, …, 53`. Mỗi vòng:

| Bước           | Code                                              | Kết quả với `i = 0`                                                        |
| -------------- | ------------------------------------------------- | -------------------------------------------------------------------------- |
| Lấy dict       | `nd = nodes_data[0]`                              | `{"id": 0, "name": "Cong Parabol", "x": 92, "y": 351, "type": "Building"}` |
| Tạo Node       | `Node(0, "Cong Parabol", 92, 351, "Building")`    | `id=0`, `name`, `x`, `y`, `type`                                           |
| Gắn vào đồ thị | `graph.addNode(node)`                             | xem bên dưới                                                               |

`Node.id` = `i` = vị trí trong list. Field `"id"` trong JSON luôn khớp `i` (user không tự đặt id).

**`graph.addNode(node)`** (`graph.py` dòng 22–24):

```python
graph.nodes.append(node)      # nodes[0] = Node(...)
graph.adjList.append([])      # adjList[0] = []  — list kề rỗng, chờ cạnh
```

Sau **một** vòng (`i=0`): `len(graph.nodes)==1`, `len(graph.adjList)==1`, `adjList[0]==[]`.

Sau **hết** vòng (54 lần):

- `graph.nodes` — list 54 `Node`; truy cập `graph.nodes[i]` bằng `id` `i`.
- `graph.adjList` — list 54 list rỗng; `adjList[i]` sẽ chứa các `Edge` xuất phát từ `id` `i`.

---

#### 5.3.3. Vòng tạo cạnh

```23:34:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\loader.py
    node_count = len(graph.nodes)
    for ed in edges_data:
        u = ed["from"]
        v = ed["to"]
        if u < 0 or u >= node_count or v < 0 or v >= node_count:
            continue
        x1, y1 = graph.nodes[u].x, graph.nodes[u].y
        x2, y2 = graph.nodes[v].x, graph.nodes[v].y
        weight = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        graph.addEdge(Edge(u, v, weight))
        if ed.get("bidirectional", True):
            graph.addEdge(Edge(v, u, weight))
```

Mỗi `ed` là một dict từ `edges.json`. Xét **cạnh đầu tiên** `{"from": 0, "to": 1, "bidirectional": true}`:

**Bước A — lấy `u`, `v` trực tiếp**

```
u = ed["from"]  →  0   (json.load đã parse thành int)
v = ed["to"]    →  1
```

Nếu `"from": 999` → `u >= node_count` → `continue`, cạnh không được thêm (im lặng).

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

Lặp cho 66 cạnh JSON → nhiều hơn 66 `Edge` object trong `adjList` (vì hầu hết hai chiều). Một node như id `0` có thể có nhiều neighbor trong `adjList[0]`.

---

#### 5.3.4. Giá trị trả về

```36:36:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\loader.py
    return graph, Navigator(graph)
```

| Thành phần         | Là gì       | Trạng thái sau `return`                                            |
| ------------------ | ----------- | ------------------------------------------------------------------ |
| `graph`            | `Graph`     | 54 node, `adjList` đầy cạnh có trọng số                            |
| `Navigator(graph)` | `Navigator` | `navigator.graph` trỏ **cùng** object `graph`; chưa gọi `dijkstra` |

`CampusMap.load()` nhận hai giá trị này ở dòng 19 `map.py`, gán `self._graph`, `self._navigator`.

**Chuỗi gọi tóm tắt:**

```text
loadData(nodes_path, edges_path)
  → json.load × 2
  → vòng Node: Graph.nodes + Graph.adjList (list rỗng)
  → vòng Edge: u/v từ JSON → weight → addEdge (×2 nếu bidirectional)
  → return (graph, Navigator(graph))
```

Gặp `Navigator(graph)` — mở `core/navigator.py` _(mục 5.3.5)_.

---

#### 5.3.5. `Navigator` và `MinHeap` (`core/navigator.py`) — ý tưởng chung

**Ý tưởng:** `Graph` giữ dữ liệu (node, cạnh, `adjList`). `Navigator` giữ **thuật toán tìm đường** chạy trên `Graph` đó — tách “bản đồ” và “cách đi trên bản đồ”. Lúc nạp graph chỉ **gắn** hai phần lại; chưa tính đường.

| Class       | Vai trò                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------ |
| `MinHeap`   | Hàng đợi ưu tiên — mỗi bước Dijkstra lấy đỉnh có khoảng cách tạm nhỏ nhất (`push` / `pop`) |
| `Navigator` | Bọc Dijkstra: nhận `Graph`, cung cấp `dijkstra` và `getPath`                               |

**Lúc `loadData` — chỉ `Navigator.__init__`:**

|            |                                                   |
| ---------- | ------------------------------------------------- |
| **Input**  | `graph` — object `Graph` vừa xây xong             |
| **Làm gì** | `self.graph = graph` (cùng reference, không copy) |
| **Output** | Instance `Navigator` → `CampusMap._navigator`     |

Chưa gọi `dijkstra` hay `getPath`; chưa dùng `MinHeap`.

**Khi tìm đường** (`find_shortest_path`, mục 6) — `Navigator` được dùng:

| Hàm                                     | Input                                       | Làm gì                                                              | Output                                            |
| --------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------- |
| `dijkstra(start_idx, end_idx)`          | id nguồn, id đích (vd. `0`, `25`)           | Duyệt `graph.adjList` qua `MinHeap`; cập nhật khoảng cách ngắn nhất | `distances`, `previous` — hai list length 54      |
| `getPath(end_idx, previous)`            | id đích + `previous` từ `dijkstra`           | Dựng lại thứ tự id trên đường đi                                    | `path_idx` — list id, vd. `[0,1,2,3,4,5,6,25]` |

`CampusMap` trả `path_idx` thẳng về UI (không đổi kiểu). Chi tiết từng bước vòng lặp: mục 6.3 và 6.4.

---

### 5.4. `Graph` trong bộ nhớ sau `reload_graph`

Một nguồn dữ liệu node duy nhất — `CampusMap._graph.nodes` (list `Node`), UI truy cập qua property `CampusMap.nodes`:

```59:61:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\map.py
    @property
    def nodes(self):
        return self._graph.nodes
```

| Thuộc tính `Node` | Kiểu    | Ví dụ node đầu      |
| ----------------- | ------- | ------------------- |
| `id`              | `int`   | `0`                 |
| `name`            | `str`   | `"Cong Parabol"`    |
| `x`, `y`          | `int`   | `92`, `351`         |
| `type`            | `str`   | `"Building"`        |

Ví dụ node `id = 0`: tọa độ `(92, 351)`, cạnh kề trong `graph.adjList[0]` — list các `Edge(from_node=0, to_node=..., weight=...)`.

Kết thúc `reload_graph`, `self.graph` trong `DijkstraMapApp` trỏ tới `CampusMap` đã nạp xong. Combobox được điền chuỗi dạng `"0 - Cong Parabol"` qua `get_node_options()` — phục vụ chọn điểm; `_selected_id()` tách phần số phía trước `" - "` thành chuỗi `"0"`, `"25"` rồi `find_shortest_path` ép sang `int`.

---

## 6. Tìm đường `0` → `25`

**Giả định:** `reload_graph()` đã chạy; combobox đã chọn `"0 - Cong Parabol"` và `"25 - D3"`. Bỏ qua sự kiện ấn nút — coi như `find_path()` được gọi; sau `_selected_id` có `start_id = "0"`, `end_id = "25"` (chuỗi từ combobox).

---

### 6.1. `find_path` (`main.py`)

```103:126:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\main.py
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
```

**Dòng 104–105** — Lấy ID từ combobox:

- `self.start_var.get()` → `"0 - Cong Parabol"`
- `_selected_id(...)` (dòng 153–155): tách chuỗi tại `" - "`, lấy phần đầu → `start_id = "0"`, `end_id = "25"` (chuỗi)

**Dòng 112** — Gọi thuật toán:

```python
path_ids, distance = self.graph.find_shortest_path("0", "25")
```

`self.graph` là `CampusMap`; dòng này nhảy sang `core/map.py` _(mục 6.2)_ — bên trong `find_shortest_path` ép `"0"` → `0`, `"25"` → `25`.

**Sau khi có kết quả** (với ví dụ này):

| Dòng    | Code                         | Thuật toán / UI              |
| ------- | ---------------------------- | ---------------------------- |
| 117     | `redraw_map()`               | UI — xóa vẽ cũ               |
| 123     | `get_coordinates(path_ids)`  | Đổi id → tọa độ để vẽ        |
| 124     | `_draw_path(points)`         | UI — vẽ đường đỏ             |
| 125–126 | `distance_var`, `status_var` | UI — hiển thị kết quả        |

Kết quả thuật toán cho ví dụ: `path_ids = [0, 1, 2, 3, 4, 5, 6, 25]`, `distance = 501.63527840068963` px. Dòng 126 `str(node_id)` để hiển thị `"0 -> 1 -> ... -> 25"` trên UI.

---

### 6.2. `find_shortest_path` (`core/map.py`)

```21:32:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\map.py
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
        path_idx = self._navigator.getPath(v, previous)
        return path_idx, distances[v]
```

**Input:** `start_id = "0"`, `end_id = "25"` (chuỗi từ combobox).

| Dòng  | Code                              | Input / xử lý | Output                                              |
| ----- | --------------------------------- | ------------- | --------------------------------------------------- |
| 22    | `u = int(start_id)`               | `"0"`         | `u = 0`                                             |
| 23    | `v = int(end_id)`                 | `"25"`        | `v = 25`                                            |
| 24–27 | kiểm tra `0 <= u, v < 54`         |               | hợp lệ — không ném lỗi                              |
| 28    | `self._navigator.dijkstra(0, 25)` | id            | `distances`, `previous` _(mục 6.3)_                 |
| 29–30 | `distances[25] == inf?`           |               | `False` — có đường đi                               |
| 31    | `getPath(25, previous)`          |               | `path_idx = [0,1,2,3,4,5,6,25]` _(mục 6.4)_         |
| 32    | `return`                          |               | `([0,1,2,3,4,5,6,25], 501.63527840068963)`          |

Từ đây trở đi mọi thao tác trên đồ thị dùng **id** (số nguyên) — `Navigator` chỉ làm việc với `Graph.adjList`.

---

### 6.3. `Navigator.dijkstra(0, 25)` (`core/navigator.py`)

```37:59:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\navigator.py
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

**Input:** `start_idx = 0`, `end_idx = 25`.

**Output:** hai list length 54 — `distances` (khoảng cách ngắn nhất từ `0` tới mỗi đỉnh) và `previous` (đỉnh đứng ngay trước trên đường tối ưu).

---

#### Khởi tạo (dòng 38–43)

| Dòng | Code | Sau khi chạy |
| ---- | ---- | ------------ |
| 38 | `n = len(self.graph.nodes)` | `n = 54` |
| 39 | `distances = [float("inf")] * n` | 54 phần tử, toàn `inf` |
| 40 | `previous = [-1] * n` | 54 phần tử, toàn `-1` |
| 41 | `distances[start_idx] = 0` | `distances[0] = 0` |
| 42 | `pq = MinHeap()` | heap rỗng |
| 43 | `pq.push(0, start_idx)` | `pq.heap = [[0, 0]]` |

`distances[i]` giữ khoảng cách tạm thời tới đỉnh `i`. `previous[i]` ghi đỉnh liền trước `i` trên đường đang tốt nhất. `pq` (MinHeap) chứa các cặp `[khoảng_cách, id]` chờ xử lý — mỗi lần `pop()` lấy cặp có khoảng cách nhỏ nhất.

---

#### Mỗi vòng `while` làm gì (dòng 44–58)

Điều kiện vào vòng: `len(pq.heap) > 0` (dòng 44).

Mỗi lần lặp chạy **theo thứ tự cố định** trong code:

```text
pq.pop()                          → current_item = [current_dist, u]
if u == end_idx: break            → dừng nếu đã tới đích
if current_dist > distances[u]:   → continue (bỏ qua, sang vòng sau)
for edge in getNeighbors(u):      → duyệt từng cạnh kề
    v = edge.to_node
    new_dist = current_dist + edge.weight
    if new_dist < distances[v]:   → cập nhật distances, previous, pq.push
return distances, previous
```

Phần còn lại của mục này minh họa **4 vòng lặp** tiêu biểu (toàn bộ chạy thực tế có 27 lần `pop`).

---

#### Vòng lặp 1 — `pop` ra đỉnh `0`

**Dòng 45–47:**

```python
current_item = pq.pop()    # → [0, 0]
current_dist = 0
u = 0
```

**Dòng 48–49:** `u == end_idx`? `0 == 25` → `False`, không `break`.

**Dòng 50–51:** `current_dist > distances[u]`? `0 > distances[0]=0` → `False`, không `continue`.

**Dòng 52–58 — vòng `for`:** `getNeighbors(0)` trả **một** cạnh: `Edge(to_node=1, weight≈132.0038)`.

Lần lặp `for` đầu tiên (và duy nhất):

| Dòng | Biểu thức | Giá trị |
| ---- | --------- | ------- |
| 53 | `v = edge.to_node` | `v = 1` |
| 54 | `new_dist = current_dist + edge.weight` | `0 + 132.0038 = 132.0038` |
| 55 | `new_dist < distances[v]`? | `132.0038 < inf` → `True` |
| 56 | `distances[v] = new_dist` | `distances[1] = 132.0038` |
| 57 | `previous[v] = u` | `previous[1] = 0` |
| 58 | `pq.push(new_dist, v)` | heap thêm `[132.0038, 1]` |

Hết vòng `for`. Quay lại dòng 44 — heap còn phần tử, tiếp tục `while`.

---

#### Vòng lặp 2 — `pop` ra đỉnh `1`, một nhánh `if` không chạy

**Dòng 45–47:** `pop` → `current_dist = 132.0038`, `u = 1`.

**Dòng 48–51:** không `break`, không `continue`.

**Dòng 52 — `getNeighbors(1)`** trả 3 cạnh: tới `0`, `2`, `47`.

**Lần `for` thứ nhất** — cạnh tới `v = 0`:

| Dòng | Biểu thức | Giá trị |
| ---- | --------- | ------- |
| 54 | `new_dist` | `132.0038 + 132.0038 = 264.0076` |
| 55 | `new_dist < distances[0]`? | `264.0076 < 0` → `False` |

Khối dòng 56–58 **không chạy** — `distances`, `previous`, `pq` giữ nguyên cho đỉnh `0`. (Đây là trường hợp đã có đường ngắn hơn tới `0`; trong sách giáo khoa hay gọi là không *relax* cạnh này, nhưng code chỉ đơn giản là điều kiện `if` ở dòng 55 sai.)

**Lần `for` thứ hai** — cạnh tới `v = 2`: `new_dist = 162.0038 < inf` → dòng 56–58 chạy → `distances[2]=162.0038`, `previous[2]=1`, `pq.push(162.0038, 2)`.

**Lần `for` thứ ba** — cạnh tới `v = 47`: tương tự → `distances[47]=202.0109`, `previous[47]=1`, `pq.push(202.0109, 47)`.

Các vòng `pop` tiếp theo (đỉnh `2`, `47`, `3`, `4`, `5`, …) lặp lại cùng khung dòng 45–58; heap luôn có thể chứa **nhiều bản ghi** cho cùng một đỉnh (do mỗi lần dòng 58 `push` thêm, không xóa bản cũ).

---

#### Vòng lặp minh họa — `continue` ở dòng 50–51

Ở một vòng sau (lần `pop` thứ 23 trong trace đầy đủ), heap trả về:

```python
current_dist = 432.7171
u = 14
```

Nhưng `distances[14]` đã được cập nhật thành `420.9499` ở vòng trước (qua đường khác rẻ hơn).

**Dòng 50–51:**

```python
if current_dist > distances[u]:   # 432.7171 > 420.9499 → True
    continue
```

Vòng lặp `while` **nhảy thẳng** về dòng 44 — không vào `for edge in ...`. Bản ghi `[432.7171, 14]` trong heap là **cũ** (khoảng cách đã lỗi thời); thuật toán textbook gọi là *stale entry*, nhưng trong code chỉ có một nhánh `if` + `continue`.

---

#### Vòng lặp — `pop` ra đỉnh `6`, gán `distances[25]`

Sau nhiều vòng, một lần `pop` trả về `current_dist = 447.2570`, `u = 6`. Điều kiện dòng 48–51 không chặn.

`getNeighbors(6)` có 7 cạnh. Minh họa cạnh tới **đích** `v = 25`:

| Dòng | Biểu thức | Giá trị |
| ---- | --------- | ------- |
| 53 | `v = edge.to_node` | `25` |
| 54 | `new_dist` | `447.2570 + 54.3783 = 501.6353` |
| 55 | `new_dist < distances[25]`? | `501.6353 < inf` → `True` |
| 56–58 | cập nhật + push | `distances[25]=501.6353`, `previous[25]=6`, `pq.push(501.6353, 25)` |

Các cạnh khác của đỉnh `6` (tới `5`, `7`, `23`, …) vẫn chạy cùng khối `for`; nhiều cái rơi vào trường hợp dòng 55 `False` (đã có `distances[v]` nhỏ hơn).

---

#### Vòng lặp cuối — `break` ở dòng 48–49

Heap cuối cùng `pop` ra:

```python
current_dist = 501.6353
u = 25
```

**Dòng 48–49:**

```python
if u == end_idx:    # 25 == 25 → True
    break
```

Vòng `while` kết thúc. Các phần tử còn trong heap không được xử lý — không cần vì đã tìm được đường tới đích.

---

#### `return` (dòng 59)

```python
return distances, previous
```

Kết quả liên quan ví dụ `0 → 25`:

- `distances[25] = 501.63527840068963`
- Trên đường tối ưu: `previous[25]=6` → `previous[6]=5` → `previous[5]=4` → `previous[4]=3` → `previous[3]=2` → `previous[2]=1` → `previous[1]=0` → `previous[0]=-1`

Tổng cộng **27 lần `pq.pop()`** cho cặp `(0, 25)`; dừng sớm nhờ `break` dòng 48–49, không duyệt hết 54 đỉnh.

---

### 6.4. `Navigator.getPath(25, previous)`

```61:70:d:\ĐHBK\2025.2\CTDL&GT\CK\Dijkstra\core\navigator.py
    def getPath(self, end_idx, previous):
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

`previous` là list length 54: `previous[i]` = đỉnh đứng ngay trước `i` trên đường tối ưu từ nguồn; `previous[0] = -1` (đỉnh xuất phát không có predecessor). Không cần truyền `start_idx` — đi ngược từ `end_idx` theo `previous` sẽ tự dừng tại `-1`.

`getPath` **dựng lại** danh sách id từ đích về nguồn rồi đảo bằng vòng `for` (dòng 67–69):

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

`find_shortest_path` trả thẳng list id: `[0, 1, 2, 3, 4, 5, 6, 25]`.

---

### 6.5. Trả về `find_path` — tóm tắt luồng

```text
find_path()
  start_id="0", end_id="25"  (chuỗi từ combobox)
  → CampusMap.find_shortest_path("0", "25")
      int("0")→0, int("25")→25
      → Navigator.dijkstra(0, 25)     → distances, previous
      → Navigator.getPath(25, previous)  → [0, 1, 2, 3, 4, 5, 6, 25]
  ← path_ids=[0, 1, 2, 3, 4, 5, 6, 25], distance=501.63527840068963
  → get_coordinates → vẽ (UI)
```

Đường đi đi theo chuỗi cạnh liên tiếp `0—1—2—3—4—5—6` rồi nhánh `6—25` — khớp với cạnh trong `edges.json`, không phải đường chim bay thẳng trên bản đồ.

---

_(Hết luồng tìm đường `0` → `25`.)_
