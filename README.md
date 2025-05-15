# Connect4AI - Trò chơi Connect 4 với AI

![Connect 4](https://img.shields.io/badge/Connect%204-Game-blue)
![AI](https://img.shields.io/badge/AI-Solver-green)
![Python](https://img.shields.io/badge/Python-FastAPI-brightgreen)
![C++](https://img.shields.io/badge/C%2B%2B-17-orange)

Một ứng dụng AI Connect 4 hiệu suất cao, sử dụng FastAPI (Python) làm backend và engine C++ tối ưu, hỗ trợ cache và Docker.

## Tính năng

- API RESTful cho trò chơi Connect 4.
- Engine C++ tối ưu, giao tiếp trực tiếp qua shared library (`.so`/`.dll`).
- Hỗ trợ cache kết quả để tăng tốc.
- Dễ dàng build và deploy bằng Docker.
- Có thể mở rộng giao diện web.

## Cấu trúc dự án

<<<<<<< HEAD
- `connect4_api.py` - API chính xử lý logic trò chơi và kết nối với AI.
- `connect4_solver.cpp` - Chương trình C++ triển khai thuật toán AI.
- `connect4_algorithm.cpp` & `connect4_algorithm.hpp` - Triển khai thuật toán giải Connect 4.
- `connect4_position.hpp` - Định nghĩa cấu trúc bàn chơi và các nước đi.
- `7x6.book` - Tệp opening book chứa các nước đi tối ưu đã được tính toán trước.
=======
```bash
.
├── app.py                  # FastAPI backend (entrypoint)
├── connect4_engine.cpp     # C++ engine (entrypoint cho AI)
├── connect4_algorithm.cpp  # Thuật toán AI
├── connect4_algorithm.hpp  # Khai báo thuật toán
├── opening_book.hpp        # Sách khai cuộc
├── transposition_table.hpp # Bảng băm trạng thái
├── move_sorter.hpp         # Sắp xếp nước đi
├── connect4_position.hpp   # Biểu diễn trạng thái bàn cờ
├── 7x6.book                # File opening book
├── connect4_cache.json     # Cache kết quả AI
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build file
└── README.md
```
>>>>>>> 6e56d9b96f150b818f77068af2f4a19a37e152d1

## Yêu cầu hệ thống

- Python 3.12+
- Docker (khuyến nghị để build và chạy nhanh)
- Compiler hỗ trợ C++17 (nếu build thủ công)

## Hướng dẫn cài đặt

### 1. Tải mã nguồn

**Cách 1:** Sử dụng Git
```bash
git clone https://github.com/Tahaian22028242/Connect4AI-Group19.git
cd Connect4AI-Group19
```

**Cách 2:** Tải trực tiếp ZIP từ GitHub
- Truy cập vào repository qua link: https://github.com/Tahaian22028242/Connect4AI-Group19
- Click chọn "Code" -> "Download ZIP".
- Giải nén file ZIP và mở thư mục.

### 2. Cài đặt thư viện Python cần thiết
```bash
pip install -r requirements.txt
```

### 3. Biên dịch engine AI C++

**Cách 1:** Dùng Docker (khuyến nghị)
```bash
docker build -t connect4ai .
docker run -p 8080:8080 connect4ai
```

**Cách 2:** Biên dịch thủ công
```bash
g++ -O3 -std=c++17 -shared -fPIC \
    connect4_algorithm.cpp connect4_engine.cpp \
    -o libconnect.so
```
*(Trên Windows, build ra connect.dll và sửa lại app.py cho phù hợp)*

### 4. Chạy ứng dụng FastAPI
```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

## Cách sử dụng

1. Đảm bảo đã build xong shared library và cài đủ Python dependencies.
2. Truy cập API tại `http://localhost:8080`.
3. Gửi yêu cầu POST đến `/api/connect4-move` với trạng thái bàn chơi hiện tại.

**Ví dụ request:**
```json
{
  "board": [[0,0,0,0,0,0,0], ...],  // 6x7 ma trận
  "current_player": 1,
  "valid_moves": [0,1,2,3,4,5,6],
  "is_new_game": false
}
```

**Response:**
```json
{
  "move": 3,
  "total_elapsed": 0.0123
}
```

**Test**:
- **GET** `/api/test` : Kiểm tra server hoạt động.

## Triển khai public với Ngrok

Để server của bạn có thể truy cập được từ internet, bạn có thể sử dụng Ngrok:

1. Tải và cài đặt Ngrok: https://ngrok.com/download
2. Trong terminal của Ngrok (ngrok.exe), chạy lệnh:
```bash
ngrok http 8000 # hoặc cổng khác tương ứng, số cổng nằm trong file app.py
```
4. Sao chép URL Forwarding (dạng https://xxxx-xxxx.ngrok-free.app) và đăng ký với server chính.

Xem thêm hướng dẫn tạo API public chi tiết cho chương trình: https://github.com/quyk67uet/setup_connect4/blob/main/README.md

## Giải thích thuật toán AI

AI sử dụng kết hợp giữa:
1. **Opening Book:** Sử dụng các nước đi tối ưu đã được tính toán trước.
2. **Solver:** Phân tích trạng thái hiện tại để tìm nước đi tốt nhất.
3. **Đánh giá nước đi:** Tính toán điểm số cho từng nước đi khả dụng và chọn nước đi có điểm cao nhất (nếu nhiều nước đi tốt ngang nhau sẽ chọn ngẫu nhiên).

## Ghi chú

- AI sẽ chọn ngẫu nhiên giữa các nước đi tốt nhất nếu có nhiều lựa chọn ngang điểm.
- Cache được lưu trong RAM và định kỳ ghi ra file `connect4_cache.json`.
- Nếu muốn giữ cache lâu dài, mount volume Docker hoặc copy file cache ra ngoài.

## Giấy phép

[Hướng dẫn từng bước để xây dựng AI Connect 4 hoàn hảo](http://blog.gamesolver.org).

---

© 2025 Connect4AI Group 19
