import csv
import hashlib
import sqlite3
from pathlib import Path

from database import PROJECT_ROOT, get_database_path


SEED_MANAGER_EMAIL = "walking-skeleton-manager@smashgo.local"
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
COURTS_PATH = PROJECT_ROOT / "data" / "courts.csv"


def initialize_database(database_path: Path | None = None) -> int:
    target_path = database_path or get_database_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(target_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        demo_hash = hashlib.pbkdf2_hmac(
            "sha256", b"disabled-walking-skeleton-account", b"smashgo-seed", 100_000
        ).hex()
        connection.execute(
            """
            INSERT OR IGNORE INTO Users (FullName, Email, PasswordHash, Role)
            VALUES (?, ?, ?, 'MANAGER')
            """,
            ("SmashGo Demo Manager", SEED_MANAGER_EMAIL, demo_hash),
        )
        manager_id = connection.execute(
            "SELECT UserID FROM Users WHERE Email = ?", (SEED_MANAGER_EMAIL,)
        ).fetchone()[0]

        with COURTS_PATH.open(encoding="utf-8-sig", newline="") as seed_file:
            courts = list(csv.DictReader(seed_file))

        for court in courts:
            connection.execute(
                """
                INSERT INTO Court (
                    ManagerID, CourtName, Location, Description, PricePerHour,
                    OpenTime, CloseTime, Status
                )
                SELECT ?, ?, ?, ?, ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM Court WHERE ManagerID = ? AND CourtName = ?
                )
                """,
                (
                    manager_id,
                    court["CourtName"],
                    court["Location"],
                    court["Description"],
                    court["PricePerHour"],
                    court["OpenTime"],
                    court["CloseTime"],
                    court["Status"],
                    manager_id,
                    court["CourtName"],
                ),
            )
            court_id = connection.execute(
                "SELECT CourtID FROM Court WHERE ManagerID = ? AND CourtName = ?",
                (manager_id, court["CourtName"]),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO Court_Image (CourtID, Url, SortOrder)
                SELECT ?, ?, 0
                WHERE NOT EXISTS (
                    SELECT 1 FROM Court_Image WHERE CourtID = ? AND Url = ?
                )
                """,
                (court_id, court["ImageUrl"], court_id, court["ImageUrl"]),
            )

        return connection.execute("SELECT COUNT(*) FROM Court").fetchone()[0]


if __name__ == "__main__":
    court_count = initialize_database()
    print(f"Database ready: {court_count} courts in {get_database_path()}")