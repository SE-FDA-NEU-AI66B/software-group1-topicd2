import csv
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

from database import PROJECT_ROOT, get_database_path
from werkzeug.security import generate_password_hash

SEED_MANAGER_EMAIL = "walking-skeleton-manager@smashgo.local"
DEMO_BOOKING_OWNER_EMAIL = "user2@smashgo.local"
# A confirmed booking on the first court, tomorrow 20:00-22:00, so the
# double-booking rejection (BR1, US-05) can be demonstrated right after setup.
DEMO_BOOKING_START = "20:00"
DEMO_BOOKING_END = "22:00"
SEED_USERS = (
    {
        "full_name": "SmashGo Demo User",
        "email": "user@smashgo.local",
        "password": "UserTest123!",
        "role": "USER",
    },
    {
        "full_name": "SmashGo Demo User 2",
        "email": DEMO_BOOKING_OWNER_EMAIL,
        "password": "User2Test123!",
        "role": "USER",
    },
    {
        "full_name": "SmashGo Demo Manager",
        "email": SEED_MANAGER_EMAIL,
        "password": "ManagerTest123!",
        "role": "MANAGER",
    },
    {
        "full_name": "SmashGo Demo Admin",
        "email": "admin@smashgo.local",
        "password": "AdminTest123!",
        "role": "ADMIN",
    },
)
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
COURTS_PATH = PROJECT_ROOT / "data" / "courts.csv"


def initialize_database(database_path: Path | None = None) -> int:
    target_path = database_path or get_database_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(target_path)) as connection, connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        for seed_user in SEED_USERS:
            connection.execute(
                """
                INSERT INTO Users (FullName, Email, PasswordHash, Role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(Email) DO UPDATE SET
                    FullName = excluded.FullName,
                    PasswordHash = excluded.PasswordHash,
                    Role = excluded.Role
                """,
                (
                    seed_user["full_name"],
                    seed_user["email"],
                    generate_password_hash(seed_user["password"]),
                    seed_user["role"],
                ),
            )

        manager_id = connection.execute(
            "SELECT UserID FROM Users WHERE Email = ? COLLATE NOCASE",
            (SEED_MANAGER_EMAIL,),
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

        seed_demo_booking(connection)
        return connection.execute("SELECT COUNT(*) FROM Court").fetchone()[0]


def seed_demo_booking(connection: sqlite3.Connection) -> None:
    owner_id = connection.execute(
        "SELECT UserID FROM Users WHERE Email = ? COLLATE NOCASE",
        (DEMO_BOOKING_OWNER_EMAIL,),
    ).fetchone()[0]
    court_id, price_per_hour = connection.execute(
        "SELECT CourtID, PricePerHour FROM Court WHERE Status = 'ACTIVE' ORDER BY CourtID LIMIT 1"
    ).fetchone()
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    total_amount = price_per_hour * 2
    connection.execute(
        """
        INSERT INTO Booking (
            UserID, CourtID, BookingDate, StartTime, EndTime,
            TotalAmount, DepositAmount, Status
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED'
        WHERE NOT EXISTS (
            SELECT 1 FROM Booking
            WHERE CourtID = ? AND BookingDate = ?
              AND StartTime < ? AND EndTime > ?
              AND Status IN ('PENDING', 'CONFIRMED', 'CHECKED_IN')
        )
        """,
        (
            owner_id,
            court_id,
            booking_date,
            DEMO_BOOKING_START,
            DEMO_BOOKING_END,
            total_amount,
            total_amount,
            court_id,
            booking_date,
            DEMO_BOOKING_END,
            DEMO_BOOKING_START,
        ),
    )


if __name__ == "__main__":
    court_count = initialize_database()
    print(f"Database ready: {court_count} courts in {get_database_path()}")