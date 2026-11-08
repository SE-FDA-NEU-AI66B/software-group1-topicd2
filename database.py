import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


def get_database_path() -> Path:
    configured_path = Path(os.getenv("DATABASE_PATH", "instance/smashgo.sqlite3"))
    if not configured_path.is_absolute():
        configured_path = PROJECT_ROOT / configured_path
    return configured_path


def get_db_connection(database_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(database_path) if database_path is not None else get_database_path()
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def check_database(database_path: str | Path) -> None:
    """Raise sqlite3.Error if the database file is missing or unreadable.

    mode=rw stops SQLite from creating an empty file at a wrong path, and
    reading sqlite_master fails on a file that is not a database.
    """
    uri = Path(database_path).resolve().as_uri() + "?mode=rw"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("SELECT count(*) FROM sqlite_master").fetchone()
    finally:
        connection.close()