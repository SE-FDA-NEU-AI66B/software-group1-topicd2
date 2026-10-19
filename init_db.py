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
HISTORY_OWNER_EMAIL = "user@smashgo.local"
# Bookings of the main test user in several states, for the /my-bookings demo.
# (court index, days from today, start, end, booking status, payment status)
HISTORY_BOOKINGS = (
    (1, 3, "18:00", "20:00", "CONFIRMED", "SUCCESS"),
    (2, -7, "19:00", "21:00", "COMPLETED", "SUCCESS"),
    (3, -2, "07:00", "08:00", "CANCELLED", "REFUNDED"),
    (4, -1, "17:00", "18:00", "EXPIRED", None),
)
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
# Task #94: Stable names make the two pending Admin demo requests idempotent across database initialization.
ADMIN_DEMO_REQUESTS = (
    {
        "court_name": "SmashGo Demo Court Request 1",
        "location": "12 Nguyễn Khánh Toàn, Cầu Giấy, Hà Nội",
        "description": "Sân demo mới chờ quản trị viên duyệt.",
        "price_per_hour": 90000,
        "open_time": "06:00",
        "close_time": "23:00",
    },
    {
        "court_name": "SmashGo Demo Court Request 2",
        "location": "25 Thái Hà, Đống Đa, Hà Nội",
        "description": "Sân demo thứ hai để kiểm tra quy trình từ chối.",
        "price_per_hour": 100000,
        "open_time": "05:30",
        "close_time": "22:30",
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
        seed_booking_history(connection)
        # Task #94: Seed pending requests and images so Admin review can be demonstrated after setup.
        seed_admin_court_requests(connection, manager_id, courts[0]["ImageUrl"])
        return connection.execute("SELECT COUNT(*) FROM Court").fetchone()[0]


# Task #94: Seed two pending CREATE requests without duplicating them on repeated initialization.
def seed_admin_court_requests(
    connection: sqlite3.Connection, manager_id: int, image_url: str
) -> None:
    for demo_request in ADMIN_DEMO_REQUESTS:
        existing = connection.execute(
            """
            SELECT RequestID FROM Court_Request
            WHERE ManagerID = ? AND CourtName = ?
            """,
            (manager_id, demo_request["court_name"]),
        ).fetchone()
        if existing:
            continue

        cursor = connection.execute(
            """
            INSERT INTO Court_Request (
                ManagerID, RequestType, CourtName, Location, Description,
                PricePerHour, OpenTime, CloseTime, Status
            ) VALUES (?, 'CREATE', ?, ?, ?, ?, ?, ?, 'PENDING')
            """,
            (
                manager_id,
                demo_request["court_name"],
                demo_request["location"],
                demo_request["description"],
                demo_request["price_per_hour"],
                demo_request["open_time"],
                demo_request["close_time"],
            ),
        )
        connection.execute(
            """
            INSERT INTO Court_Request_Image (RequestID, Url, SortOrder)
            VALUES (?, ?, 0)
            """,
            (cursor.lastrowid, image_url),
        )


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



def seed_booking_history(connection: sqlite3.Connection) -> None:
    owner_id = connection.execute(
        "SELECT UserID FROM Users WHERE Email = ? COLLATE NOCASE",
        (HISTORY_OWNER_EMAIL,),
    ).fetchone()[0]
    if connection.execute("SELECT 1 FROM Booking WHERE UserID = ?", (owner_id,)).fetchone():
        return

    connection.execute(
        """
        INSERT INTO BankAccount (
            UserID, BankName, AccountNumber, AccountHolderName, IsVerified, VerifiedAt
        )
        SELECT ?, 'Vietcombank', '0123456789', 'SMASHGO DEMO USER', 1, CURRENT_TIMESTAMP
        WHERE NOT EXISTS (
            SELECT 1 FROM BankAccount
            WHERE UserID = ? AND BankName = 'Vietcombank' AND AccountNumber = '0123456789'
        )
        """,
        (owner_id, owner_id),
    )
    bank_account_id = connection.execute(
        "SELECT BankAccountID FROM BankAccount WHERE UserID = ? AND AccountNumber = '0123456789'",
        (owner_id,),
    ).fetchone()[0]
    courts = connection.execute(
        "SELECT CourtID, PricePerHour FROM Court WHERE Status = 'ACTIVE' ORDER BY CourtID"
    ).fetchall()

    for court_index, day_offset, start, end, status, payment_status in HISTORY_BOOKINGS:
        court_id, price_per_hour = courts[court_index]
        booking_date = date.today() + timedelta(days=day_offset)
        hours = (int(end[:2]) - int(start[:2])) + (int(end[3:]) - int(start[3:])) / 60
        amount = round(price_per_hour * hours)
        cursor = connection.execute(
            """
            INSERT INTO Booking (
                UserID, CourtID, BookingDate, StartTime, EndTime, TotalAmount,
                DepositAmount, Status, HoldExpiresAt, CancelledAt, CancelledBy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                owner_id,
                court_id,
                booking_date.isoformat(),
                start,
                end,
                amount,
                amount,
                status,
                f"{booking_date - timedelta(days=1)} 12:10:00" if status == "EXPIRED" else None,
                f"{booking_date - timedelta(days=1)} 09:00:00" if status == "CANCELLED" else None,
                owner_id if status == "CANCELLED" else None,
            ),
        )
        if payment_status:
            connection.execute(
                """
                INSERT INTO Payment (
                    BookingID, BankAccountID, Amount, PaymentMethod, TransactionCode,
                    Status, RefundAmount, PaidAt, RefundedAt
                ) VALUES (?, ?, ?, 'BANK_TRANSFER', ?, ?, ?, ?, ?)
                """,
                (
                    cursor.lastrowid,
                    bank_account_id,
                    amount,
                    f"SEED-{cursor.lastrowid:06d}",
                    payment_status,
                    amount if payment_status == "REFUNDED" else None,
                    f"{booking_date - timedelta(days=2)} 10:00:00",
                    f"{booking_date - timedelta(days=1)} 09:00:00"
                    if payment_status == "REFUNDED"
                    else None,
                ),
            )


if __name__ == "__main__":
    court_count = initialize_database()
    print(f"Database ready: {court_count} courts in {get_database_path()}")
