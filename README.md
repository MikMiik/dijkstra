# Dijkstra Map Desktop

Ứng dụng tìm đường ngắn nhất trên bản đồ ĐHBK. Giao diện Tkinter; thuật toán Dijkstra + MinHeap tự cài; dữ liệu `data/nodes.json`, `data/edges.json`.

## Yêu cầu

- Python 3
- Pillow: `pip install pillow`
- Tkinter (thường có sẵn khi cài Python trên Windows)

## Cài đặt và chạy

```bash
cd Dijkstra
pip install pillow
python main.py
```

Thư mục `data/` cần có:

| File | Mô tả |
|------|--------|
| `nodes.json` | Danh sách đỉnh: `id`, `name`, `x`, `y`, `type` |
| `edges.json` | Danh sách cạnh: `from`, `to`, `bidirectional` |
| `map.jpg` | Ảnh bản đồ (tọa độ node trùng pixel trên ảnh) |

Thiếu `map.jpg` vẫn mở được app nhưng không có nền ảnh; node và cạnh vẫn vẽ trên canvas.

## Cách dùng

### 1. Tìm đường (chế độ mặc định)

1. Chọn **Chế độ → Chạy**.
2. Ở thanh công cụ, chọn **Tu** và **Den** trong combobox (dạng `id - tên`, ví dụ `0 - Cong Parabol`, `25 - ...`).
3. Bấm **Tìm đường**.
4. Kết quả:
   - Đường đi: nét đỏ, điểm vàng trên canvas.
   - **Tổng khoảng cách** (px) ở panel bên phải.
   - Dãy id lộ trình ở dòng trạng thái phía dưới.

Không có đường nối giữa hai đỉnh → thông báo *Không tìm thấy đường đi*.

**Xóa vẽ**: bấm **Xóa vẽ** để xóa đường tìm được, giữ nguyên bản đồ và các node/cạnh.

### 2. Thêm node trên bản đồ

1. Chọn **Chế độ → Đánh dấu**.
2. Click một vị trí trên canvas.
3. Điền **ID** (không trùng id đã có), **Tên node**, **Loại** (`Building` hoặc `Waypoint`).
4. Node được ghi vào `data/nodes.json` và bản đồ tự tải lại.

- **Building**: chấm xanh lá.
- **Waypoint**: chấm đen.

### 3. Thêm cạnh

1. Panel phải → **Thêm cạnh**.
2. Chọn **Đỉnh 1** và **Đỉnh 2** (cùng danh sách combobox).
3. Bấm **Lưu cạnh 2 chiều** → ghi vào `data/edges.json` (hai chiều, trọng số = khoảng cách Euclidean giữa hai tọa độ).

Cạnh trùng đã có sẽ không thêm lại.

### 4. Tải lại dữ liệu

Sau khi sửa tay `nodes.json` / `edges.json` hoặc thêm node/cạnh từ app, bấm **Tải lại dữ liệu** để đồng bộ đồ thị và combobox.

Khi mở app, dữ liệu cũng được nạp tự động một lần.

## Định danh

| Khái niệm | Ý nghĩa |
|-----------|---------|
| `id` / key | Mã trong JSON và combobox; dùng khi chọn Tu/Den |
| `index` | Chỉ số nội bộ trong thuật toán (0..n-1), không nhập trên UI |

Trọng số cạnh luôn tính từ tọa độ `(x, y)` trên ảnh, không lưu sẵn trong JSON.

## Cấu trúc mã

```
Dijkstra/
├── main.py
├── core/
│   ├── map.py         # CampusMap — nạp JSON, API cho UI
│   ├── graph.py       # Node, Edge, Graph — danh sách kề
│   ├── loader.py
│   └── navigator.py   # Dijkstra + MinHeap
└── data/
    ├── nodes.json
    ├── edges.json
    └── map.jpg
```

| Lớp | Vai trò |
|-----|---------|
| `CampusMap` | Ứng dụng: dict node cho UI, `find_shortest_path` |
| `Graph` | Thuật toán: `adjList`, index 0..n-1 |
| `Navigator` | Dijkstra trên `Graph` |

## Ghi chú

- Sao lưu `data/*.json` trước khi thử thêm node/cạnh.
