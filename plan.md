# Kế hoạch bài tập lớn: Hệ thống tìm đường đi ngắn nhất bằng Dijkstra

## 1. Kiến trúc và công nghệ

- Ứng dụng chạy cục bộ dạng Desktop bằng Python thuần.
- Giao diện dùng `Tkinter`; ảnh bản đồ và thao tác ảnh dùng `Pillow` (`PIL`).
- Dữ liệu lưu hoàn toàn bằng file cục bộ trong thư mục `data/`:
  - `data/map.jpg`: ảnh bản đồ tĩnh.
  - `data/nodes.json`: danh sách các đỉnh.
  - `data/edges.json`: danh sách các cạnh.
- Không dùng API framework như FastAPI/Flask.
- Không dùng web frontend.
- Không dùng thư viện thuật toán đồ thị có sẵn như NetworkX.

## 2. Cấu trúc mã nguồn

```text
Dijkstra/
+-- main.py
+-- core/
|   +-- __init__.py
|   +-- graph.py
|   +-- dijkstra.py
+-- data/
    +-- map.jpg
    +-- nodes.json
    +-- edges.json
```

- `main.py`: chứa giao diện Tkinter, quản lý trạng thái giữa chế độ đánh dấu và chế độ chạy, vẽ node/cạnh/đường đi lên Canvas.
- `core/graph.py`: đọc `nodes.json` và `edges.json`, tính trọng số cạnh bằng khoảng cách Euclidean, xây dựng danh sách kề.
- `core/dijkstra.py`: cài đặt thuật toán Dijkstra bằng `heapq` Min-Heap.

## 3. Cấu trúc dữ liệu

### 3.1. Node

Mỗi node trong `data/nodes.json` có dạng:

```json
{
  "id": "A1",
  "name": "Cổng chính",
  "x": 120,
  "y": 240,
  "type": "Building"
}
```

- `id`: mã định danh duy nhất của node.
- `name`: tên hiển thị của node.
- `x`, `y`: tọa độ pixel trên ảnh bản đồ.
- `type`: `Building` hoặc `Waypoint`.

### 3.2. Edge

Mỗi cạnh trong `data/edges.json` có dạng:

```json
{
  "from": "A1",
  "to": "W1",
  "bidirectional": true
}
```

- `from`: ID node đầu.
- `to`: ID node cuối.
- `bidirectional`: nếu là `true`, cạnh được xem là cạnh 2 chiều.

Trọng số cạnh không nhập thủ công. Chương trình tự tính bằng khoảng cách Euclidean:

```text
sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

## 4. Chế độ Đánh dấu

- Load và hiển thị ảnh `data/map.jpg` trên `Canvas`.
- Khi người dùng click lên ảnh trong chế độ Đánh dấu:
  - Lấy tọa độ pixel `(x, y)` tại vị trí click.
  - Mở dialog yêu cầu nhập:
    - ID node.
    - Tên node.
    - Loại node: `Building` hoặc `Waypoint`.
  - Kiểm tra ID không được trùng với node đã có.
  - Append node mới vào `data/nodes.json`.
  - Vẽ điểm đánh dấu trực quan lên bản đồ.

Quy tắc đặt node:

- Node `Building` nên đặt tại cổng ra vào hoặc điểm tiếp cận thực tế của tòa nhà.
- Node `Waypoint` nên đặt tại ngã ba, ngã tư, khúc cua hoặc các điểm chuyển hướng.
- Không nên đặt node ở giữa khối nhà nếu đường đi thực tế không đi qua đó.

## 5. Bổ sung quản lý cạnh trong giao diện

Ngoài yêu cầu ban đầu, ứng dụng có thêm phần “Thêm cạnh” để nhập dữ liệu thuận tiện hơn:

- Người dùng chọn `Đỉnh 1` và `Đỉnh 2` từ combobox.
- Bấm `Lưu cạnh 2 chiều`.
- Chương trình ghi cạnh vào `data/edges.json` với `bidirectional: true`.
- Sau khi lưu cạnh, chương trình tự tải lại đồ thị và vẽ lại bản đồ.

Lý do bổ sung:

- Nếu chỉ đánh dấu node mà không có cách nối cạnh trong app, người dùng phải tự sửa `edges.json` bằng tay.
- Chức năng này giúp quy trình số hóa bản đồ hoàn chỉnh hơn: đánh dấu node, nối cạnh, rồi chạy tìm đường ngay trong cùng một ứng dụng.

## 6. Chế độ Chạy

- Chương trình đọc `nodes.json` và `edges.json`, xây dựng đối tượng `Graph`.
- Đồ thị được biểu diễn bằng danh sách kề:

```python
{
    "A1": [("W1", 35.8), ("W2", 64.1)],
    "W1": [("A1", 35.8), ("B1", 52.0)]
}
```

- Giao diện cung cấp 2 combobox:
  - Node bắt đầu.
  - Node đích.
- Khi bấm `Tìm đường`:
  - Gọi thuật toán Dijkstra trong `core/dijkstra.py`.
  - Nhận danh sách ID node trên đường đi ngắn nhất.
  - Chuyển danh sách ID thành danh sách tọa độ `(x, y)`.
  - Vẽ đường đi ngắn nhất bằng `Canvas.create_line`.
  - Hiển thị tổng khoảng cách theo đơn vị pixel.

## 7. Các nút thao tác trong giao diện

- `Tìm đường`: chạy Dijkstra và vẽ đường đi ngắn nhất.
- `Xóa vẽ`: xóa phần đường đi kết quả đang hiển thị, rồi vẽ lại ảnh bản đồ, node và cạnh từ dữ liệu đang có trong bộ nhớ.
- `Tải lại dữ liệu`: đọc lại `nodes.json` và `edges.json` từ ổ đĩa, dựng lại đồ thị, cập nhật combobox, rồi vẽ lại bản đồ.
- `Lưu cạnh 2 chiều`: thêm cạnh 2 chiều giữa hai node đang chọn vào `edges.json`.

## 8. Thuật toán Dijkstra

- File triển khai: `core/dijkstra.py`.
- Dùng `heapq` làm Min-Heap.
- Không dùng thư viện đồ thị ngoài.
- Đầu vào:
  - `adjacency`: danh sách kề.
  - `start_id`: ID node bắt đầu.
  - `end_id`: ID node đích.
- Đầu ra:
  - `path_ids`: danh sách ID node theo thứ tự đường đi ngắn nhất.
  - `total_distance`: tổng trọng số đường đi.
- Nếu không tìm thấy đường đi, trả về danh sách rỗng và khoảng cách vô cực.

Độ phức tạp thời gian:

```text
O((V + E) log V)
```

Trong đó:

- `V`: số node.
- `E`: số cạnh.

## 9. Luồng sử dụng đề xuất

1. Chạy ứng dụng bằng:

```powershell
python main.py
```

2. Chọn chế độ `Đánh dấu`.
3. Click lên bản đồ để tạo các node.
4. Dùng phần `Thêm cạnh` để nối các node có đường đi thực tế.
5. Chọn chế độ `Chạy`.
6. Chọn node bắt đầu và node đích.
7. Bấm `Tìm đường`.
8. Quan sát đường đi ngắn nhất và tổng khoảng cách trên giao diện.

## 10. Kế hoạch kiểm thử

- Kiểm thử dữ liệu rỗng:
  - `nodes.json = []`.
  - `edges.json = []`.
  - App vẫn mở được và không lỗi.
- Kiểm thử thêm node:
  - Click trên bản đồ.
  - Nhập ID, tên, loại.
  - Kiểm tra node được lưu vào `nodes.json`.
- Kiểm thử ID trùng:
  - Thêm node với ID đã tồn tại.
  - App phải báo lỗi và không ghi trùng.
- Kiểm thử thêm cạnh:
  - Chọn hai node khác nhau.
  - Bấm `Lưu cạnh 2 chiều`.
  - Kiểm tra cạnh được lưu vào `edges.json`.
- Kiểm thử tìm đường:
  - Tạo một chuỗi node có cạnh nối liên tục.
  - Chọn node đầu và node cuối.
  - App phải vẽ đường đi và hiển thị tổng khoảng cách.
- Kiểm thử không có đường đi:
  - Chọn hai node không được nối bằng cạnh.
  - App phải báo không tìm thấy đường đi.
- Kiểm thử thuật toán riêng:
  - Tạo adjacency list nhỏ.
  - Gọi `shortest_path`.
  - Kiểm tra path và tổng khoảng cách trả về đúng.
