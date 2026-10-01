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

The example values work for a local run; no API keys, passwords, or other
secrets are needed. If you need to change them, `.env` contains:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Listen only on this computer. |
| `PORT` | `5000` | Local web server port. |
| `DATABASE_PATH` | `instance/smashgo.sqlite3` | SQLite database file; a relative path is based on the project root. |
| `FLASK_DEBUG` | `false` | Keep debug mode disabled for a normal run. |

Keep `.env` local; do not commit it. Git ignores this file and the generated
SQLite database.

## 4. Create and seed the database

From the repository root, run this one command. It creates the SQLite database,
creates all 13 tables, and seeds the demo manager and 12 courts with their
images:

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
