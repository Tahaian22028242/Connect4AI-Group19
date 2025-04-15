# Connect4AI - Trò chơi Connect 4 với AI

![Connect 4](https://img.shields.io/badge/Connect%204-Game-blue)
![AI](https://img.shields.io/badge/AI-Solver-green)
![Python](https://img.shields.io/badge/Python-FastAPI-brightgreen)
![C++](https://img.shields.io/badge/C%2B%2B-17-orange)

Một ứng dụng trò chơi Connect 4 với AI thông minh, được phát triển bằng Python (FastAPI) cho backend và C++ cho thuật toán AI. Dự án này kết hợp cả giao diện web và một giải thuật AI mạnh mẽ.

## Tính năng

- API RESTful cho trò chơi Connect 4.
- Thuật toán AI mạnh dựa trên opening book và phân tích trạng thái.
- Giao diện trực quan để chơi.
- Hỗ trợ chơi người với máy.

## Cấu trúc dự án

- connect4_api.py - API chính xử lý logic trò chơi và kết nối với AI.
- connect4_solver.cpp - Chương trình C++ triển khai thuật toán AI.
- connect4_algorithm.cpp & connect4_algorithm.hpp - Triển khai thuật toán giải Connect 4.
- Position.hpp - Định nghĩa cấu trúc bàn chơi và các nước đi.
- 7x6.book - Tệp opening book chứa các nước đi tối ưu đã được tính toán trước.

## Yêu cầu hệ thống

- Python 3.8+ (cho FastAPI).
- C++ Compiler hỗ trợ C++17 (g++ hoặc MSVC).
- Các thư viện Python: FastAPI, uvicorn, pydantic.

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

### 3. Biên dịch thuật toán AI C++

**Cách 1:** Sử dụng file build (khuyến nghị)

- **Windows:** Nháy đúp chuột vào file build.bat  hoặc gõ lệnh sau vào Terminal:
```bash
build.bat
```
- **Linux/macOS:** Gõ các lệnh sau vào Terminal:
```bash
chmod +x build.sh  # chỉ cần làm lần đầu, những lần sau không cần lệnh này 
./build.sh
```

**Cách 2:** Biên dịch thủ công
```bash
g++ -std=c++17 -O2 -o connect.exe connect4_solver.cpp connect4_algorithm.cpp
```

**Lưu ý:** Nếu gặp lỗi "g++ command not found", bạn cần cài đặt trình biên dịch C++:
- **Windows:** Cài đặt MinGW hoặc MSYS2 và thêm vào PATH
- **Mac:** `brew install gcc`
- **Linux:** `sudo apt install g++`

### 4. Chạy ứng dụng
```bash
python connect4_api.py
```

Sau khi chạy, ứng dụng sẽ khởi động trên cổng 8000. Nếu cổng 8000 đã được sử dụng, bạn có thể thay đổi cổng trong file connect4_api.py.

```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Cách sử dụng

1. Đảm bảo cả API Python và chương trình AI C++ đã được cài đặt đúng cách.
2. Truy cập API tại `http://localhost:<your-port-number>` (mặc định là http://localhost:8000).
3. Gửi yêu cầu POST đến `/api/connect4-move` với trạng thái bàn chơi hiện tại.
4. API sẽ gọi thuật toán AI và trả về nước đi tốt nhất.

## Triển khai public với Ngrok

Để server của bạn có thể truy cập được từ internet, bạn có thể sử dụng Ngrok:

1. Tải và cài đặt Ngrok: https://ngrok.com/download
2. Chạy server FastAPI của bạn (mặc định cổng 8080)
3. Trong terminal khác, chạy lệnh:
```bash
ngrok http 8080
```
4. Sao chép URL Forwarding (dạng https://xxxx-xxxx.ngrok-free.app) và đăng ký với server chính.

Xem thêm hướng dẫn tạo API public chi tiết cho chương trình: https://github.com/quyk67uet/setup_connect4/blob/main/README.md

## Giải thích thuật toán AI

AI sử dụng kết hợp giữa:
1. **Opening BBook:** Sử dụng các nước đi tối ưu đã được tính toán trước.
2. **Solver:** Phân tích trạng thái hiện tại để tìm nước đi tốt nhất.
3. **Đánh giá nước đi:** Tính toán điểm số cho từng nước đi khả dụng và chọn nước đi có điểm cao nhất.

## Tùy chỉnh AI

Nếu bạn muốn tích hợp thuật toán AI của riêng mình:
1. Sửa đổi file connect4_api.py để thay thế phần gọi tiến trình AI.
2. Triển khai thuật toán AI của bạn trực tiếp trong Python hoặc tạo một chương trình ngoài tuân theo cùng giao thức.

## Giấy phép

Phần mã nguồn C++ được phát hành dưới giấy phép AGPL v3. 
Để biết thêm thông tin, bạn có thể đọc [hướng dẫn từng bước để xây dựng AI Connect 4 hoàn hảo](http://blog.gamesolver.org).

---

© 2025 Connect4AI Group 19


