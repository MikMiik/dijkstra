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

| File         | Mô tả                                          |
| ------------ | ---------------------------------------------- |
| `nodes.json` | Danh sách đỉnh: `id`, `name`, `x`, `y`, `type` |
| `edges.json` | Danh sách cạnh: `from`, `to`, `bidirectional`  |
| `map.jpg`    | Ảnh bản đồ (tọa độ node trùng pixel trên ảnh)  |

Thiếu `map.jpg` vẫn mở được app nhưng không có nền ảnh; node và cạnh vẫn vẽ trên canvas.

## Cách dùng

1. Ở thanh công cụ, chọn **Từ** và **Đến** trong combobox (dạng `id - tên`, ví dụ `0 - Cong Parabol`, `25 - ...`).
2. Bấm **Tìm đường**.
3. Kết quả:
   - Đường đi: nét đỏ, điểm vàng trên canvas.
   - **Tổng khoảng cách** (px) ở panel bên phải.
   - Dãy id lộ trình ở dòng trạng thái phía dưới.

Không có đường nối giữa hai đỉnh → thông báo _Không tìm thấy đường đi_.

**Xóa vẽ**: bấm **Xóa vẽ** để xóa đường tìm được, giữ nguyên bản đồ và các node/cạnh.

Khi mở app, dữ liệu được nạp tự động từ `data/nodes.json` và `data/edges.json`.

## Định danh

`id` trong JSON, `Node.id` và combobox là một (0, 1, 2, …) — vị trí node trong danh sách.

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
├── tests/
│   ├── test_functional.py   # 11 test case chức năng
│   ├── benchmark.py         # đo tốc độ trên lưới lớn
│   └── graph_factory.py     # sinh đồ thị giả cho test
└── data/
    ├── nodes.json
    ├── edges.json
    └── map.jpg
```

| Lớp         | Vai trò                                          |
| ----------- | ------------------------------------------------ |
| `CampusMap` | Ứng dụng: dict node cho UI, `find_shortest_path` |
| `Graph`     | Thuật toán: `adjList`, index 0..n-1              |
| `Navigator` | Dijkstra trên `Graph`                            |

## Kiểm thử

Chạy trong thư mục `Dijkstra/`.

**Chức năng** — 11 test case (map thật + lõi Dijkstra/MinHeap):

```bash
python tests/test_functional.py
```

In bảng `TC | Mô tả | Kết quả | Chi tiết`. Kết thúc bằng `X/11 đạt`.

**Hiệu năng** — lưới lớn sinh trong RAM, đo thời gian trung bình `dijkstra + getPath`:

```bash
python tests/benchmark.py
python tests/benchmark.py --sizes 10,50,100,200
```

Kết quả in ra terminal và ghi `tests/ket_qua_hieu_nang.csv`. **TB Dijkstra (ms)** là chỉ số chính; bảng còn ghi thời gian sinh lưới, số lần warm-up và số lần đo.

## Ghi chú

- Nhánh `main`: chỉ tìm đường. Thêm/sửa node và cạnh dùng nhánh `develop`.
