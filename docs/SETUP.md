# SmashGo - Hướng dẫn cài đặt và chạy

Hướng dẫn này dành cho máy mới, từ lúc lấy mã nguồn đến khi mở được ứng dụng
trên trình duyệt. Các lệnh Windows dùng PowerShell; các lệnh macOS/Linux dùng
Terminal. Không cần cài máy chủ cơ sở dữ liệu hoặc Node.js.

## 1. Chuẩn bị

Cài **Git** và **Python 3.12 trở lên**. Trên Windows, chọn cài Python Launcher
(`py`) nếu trình cài đặt có tùy chọn này.

Mở terminal và kiểm tra:

**Windows (PowerShell):**

```powershell
git --version
py -3 --version
```

**macOS/Linux:**

```sh
git --version
python3 --version
```

Nếu một lệnh không được nhận diện, hãy cài công cụ tương ứng, mở terminal mới
rồi kiểm tra lại.

## 2. Tải mã nguồn và cài thư viện

Chạy các lệnh theo hệ điều hành. Môi trường `.venv` giúp thư viện của SmashGo
không ảnh hưởng các dự án Python khác. Không cần kích hoạt môi trường; các bước
sau gọi Python bên trong `.venv` trực tiếp.

**Windows (PowerShell):**

```powershell
git clone https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git
Set-Location software-group1-topicd2
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS/Linux:**

```sh
git clone https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git
cd software-group1-topicd2
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

Nếu đã có mã nguồn, bỏ qua lệnh `git clone` và mở terminal tại thư mục
`software-group1-topicd2` (thư mục chứa `app.py`).

## 3. Cấu hình và tạo dữ liệu

Tạo file cấu hình `.env` từ file mẫu ở thư mục gốc:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```sh
cp .env.example .env
```

Nếu đã có `.env`, giữ nguyên file đó và không chạy lệnh sao chép để tránh ghi
đè cấu hình hiện có.

Các giá trị mặc định phù hợp để chạy trên chính máy này:

| Tên | Giá trị mặc định | Ý nghĩa |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Chỉ nhận kết nối từ máy đang chạy ứng dụng. |
| `PORT` | `5000` | Cổng web. Nếu cổng đang bận, đổi thành `5001`. |
| `DATABASE_PATH` | `instance/smashgo.sqlite3` | Đường dẫn tệp cơ sở dữ liệu SQLite. |
| `FLASK_DEBUG` | `false` | Không bật chế độ debug khi chạy bình thường. |
| `SECRET_KEY` | `dev-only-change-me` | Khóa phiên đăng nhập; giá trị mẫu chỉ dùng cục bộ. |

Không chia sẻ hoặc commit `.env`. Không dùng khóa mẫu hay các tài khoản demo cho
môi trường thật.

Khởi tạo cơ sở dữ liệu và dữ liệu demo từ thư mục gốc:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe init_db.py
```

**macOS/Linux:**

```sh
./.venv/bin/python init_db.py
```

Lệnh tạo thư mục cơ sở dữ liệu nếu cần, tạo bảng và thêm dữ liệu mẫu. Khi thành
công, terminal báo `Database ready: ...`. Chạy lại lệnh không nhân bản các dữ
liệu demo đã được seed. Dữ liệu được lưu cục bộ tại `instance/smashgo.sqlite3`.

### Tài khoản demo

Các tài khoản này chỉ dành cho ứng dụng chạy cục bộ:

| Vai trò | Email | Mật khẩu |
| --- | --- | --- |
| User | `user@smashgo.local` | `UserTest123!` |
| User 2 | `user2@smashgo.local` | `User2Test123!` |
| Manager | `walking-skeleton-manager@smashgo.local` | `ManagerTest123!` |
| Admin | `admin@smashgo.local` | `AdminTest123!` |

Ứng dụng không kết nối ngân hàng thật. OTP demo là `123456`.

## 4. Chạy ứng dụng

Từ thư mục gốc của dự án, chạy:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe app.py
```

**macOS/Linux:**

```sh
./.venv/bin/python app.py
```

Để terminal đang chạy mở, rồi truy cập
[http://127.0.0.1:5000/courts](http://127.0.0.1:5000/courts). Trang danh sách
sân sẽ hiển thị các sân mẫu. Nhấn `Ctrl+C` trong terminal để dừng ứng dụng.

## 5. Chạy kiểm thử

Test không cần chạy ứng dụng, không cần `.env` và không dùng cơ sở dữ liệu
trong `instance/`. Mỗi test tự tạo một tệp SQLite tạm từ `schema.sql`, cố định
thời gian hiện tại và dùng cổng thanh toán giả, nên kết quả không phụ thuộc
ngày chạy.

Cài thư viện dùng cho test (gồm `pytest`), một lần sau bước 2:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

**macOS/Linux:**

```sh
./.venv/bin/python -m pip install -r requirements-dev.txt
```

Chạy toàn bộ test từ thư mục gốc:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**macOS/Linux:**

```sh
./.venv/bin/python -m pytest -v
```

Nếu đã kích hoạt `.venv`, chỉ cần gõ `pytest` hoặc `pytest -v`. Khi thành công,
dòng cuối báo `... passed` và không có `failed`.

**Tested by:** Phan Thị Anh Quỳnh, 2026-10-31, Windows 11, Python 3.13.9. Clone
mới vào thư mục trống (không có `.env`, không có `instance/`), làm theo bước 2
và bước 5 ở trên; cả `pytest` và `python -m pytest -v` đều báo 84 passed, không
phải sửa tay.

## 6. Xử lý lỗi thường gặp

- **`git`, `py`, hoặc `python3` không được nhận diện:** Cài Git/Python, kiểm tra
  đã bật Python Launcher trên Windows, sau đó mở terminal mới. Nếu `py -3`
  không dùng được nhưng `python` có sẵn trên Windows, thay `py -3` trong các
  lệnh bằng `python`.
- **Không tạo được `.venv` hoặc báo thiếu `venv`:** Cài bản Python đầy đủ từ
  python.org, rồi chạy lại lệnh tạo môi trường ở bước 2. Trên Linux, nếu hệ
  thống báo thiếu gói venv, cài gói venv dành cho đúng phiên bản Python bằng
  trình quản lý gói của hệ điều hành.
- **PowerShell chặn `Activate.ps1`:** Hướng dẫn này không cần kích hoạt môi
  trường. Hãy chạy các lệnh `.\.venv\Scripts\python.exe ...` như trên.
- **`No module named flask` hoặc `No module named dotenv`:** Từ thư mục gốc,
  cài lại thư viện bằng lệnh `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
  trên Windows, hoặc `./.venv/bin/python -m pip install -r requirements.txt`
  trên macOS/Linux. Đảm bảo dùng Python trong `.venv`, không phải Python khác.
- **Cài thư viện lỗi do mạng hoặc tải gói:** Kiểm tra Internet, proxy hoặc
  firewall; sau đó chạy lại lệnh cài thư viện ở bước 2. Không cần cài thêm
  thư viện ngoài `requirements.txt` để chạy ứng dụng.
- **Báo không tìm thấy `pip`:** Dùng Python của môi trường ảo để chạy
  `.\.venv\Scripts\python.exe -m ensurepip --upgrade` trên Windows, hoặc
  `./.venv/bin/python -m ensurepip --upgrade` trên macOS/Linux; sau đó cài lại
  thư viện như ở bước 2.
- **`Database ready` báo lỗi hoặc không tìm thấy cơ sở dữ liệu:** Đảm bảo
  terminal đang ở thư mục dự án, `.env` nằm cạnh `app.py`, và
  `DATABASE_PATH` trỏ đến đường dẫn có thể ghi. Chạy lại `init_db.py` trước
  khi chạy `app.py`; không cần tạo SQLite riêng.
- **SQLite báo `database is locked`:** Dừng các cửa sổ ứng dụng đang chạy bằng
  `Ctrl+C`, chờ một chút, rồi khởi động lại ứng dụng. Không mở đồng thời nhiều
  bản chạy trên cùng một tệp cơ sở dữ liệu.
- **Danh sách sân trống:** Dừng ứng dụng bằng `Ctrl+C`, chạy lại `init_db.py`
  từ thư mục gốc, rồi khởi động lại ứng dụng.
- **Cổng 5000 đang được sử dụng:** Đổi `PORT=5000` thành `PORT=5001` trong
  `.env`, khởi động lại ứng dụng và truy cập
  [http://127.0.0.1:5001/courts](http://127.0.0.1:5001/courts).
- **Hình sân hoặc phông chữ không tải:** Một số hình ảnh và phông chữ lấy từ
  Internet; kiểm tra kết nối mạng. Phần danh sách và thông tin sân vẫn dùng
  được khi các tài nguyên này không tải.
- **Ứng dụng thoát ngay khi khởi động:** Đọc lỗi trong terminal. Nếu lỗi nhắc
  đến cấu hình hoặc dữ liệu, xác nhận đang ở thư mục gốc, đã tạo `.env`, cài
  thư viện và khởi tạo cơ sở dữ liệu theo các bước trên. Nếu lỗi vẫn còn, lưu
  toàn bộ thông báo lỗi cùng hệ điều hành và phiên bản Python để nhóm hỗ trợ.
- **`No module named pytest`:** Chưa cài thư viện test. Chạy lệnh cài
  `requirements-dev.txt` ở bước 5.
