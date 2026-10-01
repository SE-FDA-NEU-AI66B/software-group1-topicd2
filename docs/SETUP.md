# Walking Skeleton Setup

## Requirements

- Python 3.12 or newer
- A terminal in the repository root

The walking skeleton uses Flask and SQLite. SQLite is included with Python, so
no separate database server is needed.

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

Copy `.env.example` to `.env` if you want to change the host, port, database
path, or debug mode. The defaults work without a `.env` file. `.env` and the
SQLite database are ignored by Git.

## Create and seed the database

Run this single command from the repository root:

```powershell
python init_db.py
```

The script reads `schema.sql` and creates all 13 tables from the ERD if needed.
It then creates one demo Manager, imports 12 courts from `data/courts.csv`, and
adds their images. Other ERD tables are created but remain empty in this walking
skeleton. Running the script again does not duplicate the seed data. The demo
Manager is only an owner record for the sample courts; authentication is not
implemented here.

## Run

```powershell
python app.py
```

Open `http://127.0.0.1:5000/courts`. The route selects active courts and their
first image from SQLite and renders the returned rows in the page.

## Test

```powershell
python -m pip install pytest
python -m pytest -q
```
