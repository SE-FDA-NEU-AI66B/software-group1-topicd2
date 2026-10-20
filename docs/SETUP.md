# SmashGo setup guide

Follow the steps for your operating system from a fresh clone. The commands
below assume you are using PowerShell on Windows, or a terminal on macOS/Linux.

## 1. Prerequisites

- **Git 2.30 or newer** to clone the repository.
- **Python 3.12 or newer**. The project CI currently runs on Python 3.12.
- A terminal opened in the project folder.

SQLite is included with Python; no database server is needed. Node.js is not
required because this project has no Node-based build step.

Check the installed versions:

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

If Git or Python is missing, install it from [git-scm.com](https://git-scm.com/)
or [python.org](https://www.python.org/downloads/), then reopen the terminal.
On Windows, select the Python launcher when installing Python.

## 2. Clone the project and install dependencies

Run the commands for your operating system. They create a local virtual
environment so the project's Python packages do not affect other projects.

**Windows (PowerShell):**

```powershell
git clone https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git
Set-Location software-group1-topicd2
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If PowerShell blocks activating the virtual environment with an execution policy
error, the commands above do not require activation. Alternatively, allow
activation scripts for this PowerShell process only, then activate the
environment:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\.venv\Scripts\Activate.ps1
```

This setting applies only to the current PowerShell window. If you use Windows
Command Prompt (CMD), activate the environment with
`.venv\Scripts\activate.bat` instead.

Password hashing uses `werkzeug.security`, which is included with Flask; no
additional package is required.

**macOS/Linux:**

```sh
git clone https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git
cd software-group1-topicd2
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## 3. Configure the application

Copy the example environment file to `.env` from the repository root.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```sh
cp .env.example .env
```

The example values work for a local run and do not require external API
credentials. The example session key is for local development only. If you need
to change the settings, `.env` contains:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Listen only on this computer. |
| `PORT` | `5000` | Local web server port. |
| `DATABASE_PATH` | `instance/smashgo.sqlite3` | SQLite database file; a relative path is based on the project root. |
| `FLASK_DEBUG` | `false` | Keep debug mode disabled for a normal run. |
| `SECRET_KEY` | `dev-only-change-me` | Signs login sessions. The example value is only for local development; use a private random value for any deployed environment. |

Keep `.env` local; do not commit it. Git ignores this file and the generated
SQLite database.

## 4. Create and seed the database

From the repository root, run this one command. It creates the SQLite database,
creates all 13 tables, and seeds four test accounts, 12 courts with their
images, one confirmed demo booking, four booking-history examples, and two
pending court requests for the Admin review screen (see below):

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe init_db.py
```

**macOS/Linux** (with the virtual environment activated):

```sh
python3 init_db.py
```

On a fresh clone, expect output similar to:

```text
Database ready: 12 courts in ...\instance\smashgo.sqlite3
```

The path separator in the database path differs by operating system. Running
the command again is safe and does not duplicate the seeded records.

### Tài khoản test

Các tài khoản dưới đây chỉ dùng để kiểm tra cục bộ. Mật khẩu là mật khẩu giả
cho môi trường phát triển; cơ sở dữ liệu chỉ lưu mật khẩu dưới dạng hash.

| Vai trò | Email | Mật khẩu giả |
| --- | --- | --- |
| User | `user@smashgo.local` | `UserTest123!` |
| User 2 | `user2@smashgo.local` | `User2Test123!` |
| Manager | `walking-skeleton-manager@smashgo.local` | `ManagerTest123!` |
| Admin | `admin@smashgo.local` | `AdminTest123!` |

### Admin duyệt yêu cầu thêm sân

Đăng nhập bằng tài khoản Admin rồi mở `/admin/courts`. Màn hình có hai yêu cầu
demo đang chờ duyệt và danh sách toàn bộ sân, bao gồm sân đã tạm ngưng. Có thể
duyệt yêu cầu để tạo sân mới, hoặc từ chối sau khi nhập lý do. Hai yêu cầu demo
không bị nhân bản khi chạy lại `init_db.py`.

### Lịch đặt mẫu để demo đặt trùng

`init_db.py` tạo sẵn một lịch **đã xác nhận** của `user2@smashgo.local` trên sân
đầu tiên (*SmashGo Cầu Giấy 1*), **ngày mai từ 20:00 đến 22:00** (tính theo ngày
chạy lệnh). Đăng nhập bằng `user@smashgo.local`, mở `/book`, chọn sân đó, ngày
mai, 20:00–21:30 rồi xác nhận: hệ thống từ chối và báo khung 20:00–22:00 đã có
lịch (BR1).

## 5. Start the app and verify the result

Start the development server from the repository root.

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe app.py
```

**macOS/Linux** (with the virtual environment activated):

```sh
python3 app.py
```

Keep this terminal open, then visit
[http://127.0.0.1:5000/courts](http://127.0.0.1:5000/courts). The page title
should be **“Sân cầu lông | SmashGo”** and the page should show **12** active
courts, including the court names, Hanoi addresses, opening hours, and hourly
prices. The header should say “HỆ THỐNG ĐẶT SÂN CẦU LÔNG”; the count should read
“12 SÂN ĐANG HOẠT ĐỘNG” and “12 kết quả” should appear above the list.

To stop the server, return to its terminal and press `Ctrl+C`. Court photos and
web fonts are hosted externally, so they may not load without an internet
connection; the court details should still be visible.

### Lịch đặt mẫu của tài khoản `user@smashgo.local`

Để xem màn `/my-bookings` có dữ liệu ngay, `init_db.py` tạo cho
`user@smashgo.local` một tài khoản ngân hàng đã xác minh (Vietcombank, 4 số cuối
`6789`) và 4 lịch ở các trạng thái khác nhau (ngày tính theo hôm chạy lệnh):

| Trạng thái | Ngày | Ghi chú |
| --- | --- | --- |
| Đã xác nhận | 3 ngày tới, 18:00–20:00 | Đã thanh toán; có nút **Hủy lịch** (hoàn đủ vì còn hơn 4 giờ) |
| Đã chơi | 7 ngày trước | Không hủy được |
| Đã hủy | 2 ngày trước | Đã hoàn tiền đủ |
| Hết hạn giữ chỗ | Hôm qua | Không thanh toán trong 10 phút |

Vì đã có 1 lịch sắp tới, tài khoản này chỉ đặt thêm được 1 lượt trước khi chạm
giới hạn 2 lượt (BR6). Bước này chỉ chạy khi tài khoản chưa có lịch nào, nên chạy
lại `init_db.py` không tạo trùng.

### Cổng thanh toán giả lập (mock)

Dự án không kết nối ngân hàng thật. `bank_gateway.py` giả lập ngân hàng với các
giá trị cố định để demo và test:

| Tình huống | Cách làm |
| --- | --- |
| Mã OTP khi liên kết tài khoản | Luôn là `123456` (hiệu lực 5 phút, tối đa 3 lần nhập sai) |
| Thanh toán thành công | Dùng số tài khoản bất kỳ có 6–19 chữ số, ví dụ `9704123456789` |
| Thanh toán thất bại (`PAYMENT_FAILED`) | Dùng số tài khoản kết thúc bằng `0000`, ví dụ `123450000` |

Luồng demo: giữ chỗ ở `/book` → trang thanh toán có đồng hồ đếm ngược 10 phút →
**Liên kết tài khoản mới** → nhập OTP `123456` → **Thanh toán** → chuyển sang
`/my-bookings`. Nhập sai OTP 3 lần hoặc để quá 5 phút thì phải liên kết lại để
nhận mã mới.

### Kiểm tra đặt trùng đồng thời (US-05) bằng 2 trình duyệt

1. Mở hai trình duyệt khác nhau (hoặc một cửa sổ thường và một cửa sổ ẩn danh)
   tại `http://127.0.0.1:5000/book`.
2. Trình duyệt A đăng nhập `user@smashgo.local`, trình duyệt B đăng nhập
   `user2@smashgo.local`.
3. Ở cả hai, chọn cùng một sân, cùng ngày và cùng khung giờ còn trống (ví dụ
   *SmashGo Cầu Giấy 2*, ngày mai, 15:00–17:00).
4. Bấm **Xác nhận đặt sân** ở hai trình duyệt gần như cùng lúc.

Kết quả đúng: chỉ một bên thấy "Đã giữ chỗ cho bạn", bên còn lại nhận thông
báo khung giờ đã có lịch. Trường hợp chạy song song thật sự được kiểm tra tự
động bởi `test_simultaneous_requests_for_same_slot_have_one_winner` trong
`tests/test_booking.py`.

## 6. Troubleshooting

- **Python is missing or older than 3.12:** Install Python 3.12 or newer.
  On Windows, enable the Python launcher during installation. On macOS/Linux,
  ensure `python3` runs the newly installed version; then close and reopen the
  terminal and retry the version check in Step 1.
- **`ModuleNotFoundError: No module named 'flask'`:** The dependencies were not
  installed in this project's virtual environment. From the repository root,
  rerun the install command for your operating system:

  **Windows (PowerShell):**

  ```powershell
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

  **macOS/Linux** (with `.venv` activated):

  ```sh
  python3 -m pip install -r requirements.txt
  ```
- **The server reports that port 5000 is already in use:** Stop the other
  process using that port, or change `PORT` in `.env` (for example, to `5001`)
  and open `http://127.0.0.1:5001/courts` instead.
- **The page says there are no active courts:** Stop the server, rerun
  `init_db.py` from the repository root using the virtual environment's Python,
  then start `app.py` again. Check that `DATABASE_PATH` in `.env` points to
  `instance/smashgo.sqlite3`.

## 7. Setup verification

For an optional automated check, install pytest into the virtual environment
and run the tests from the repository root:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

**macOS/Linux** (with the virtual environment activated):

```sh
python3 -m pip install pytest
python3 -m pytest -q
```

**Tested by:** Chử Vũ Anh Thư on 2026-10-01, Windows 11, Python 3.12.3,
Microsoft Edge; approximately 1 minute including reading the instructions
(the page loaded in about 1 second). On a clean machine, the documented setup
and seed succeeded, `/courts` displayed 12 courts, and rerunning `init_db.py`
did not duplicate the seed data.
