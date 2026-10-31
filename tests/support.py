"""Constants and helpers shared by the test files.

Every date here is derived from FIXED_NOW, the frozen "current time" that
tests/conftest.py installs, so no test depends on the real date.
"""

import sqlite3
from datetime import datetime, timedelta

FIXED_NOW = datetime(2030, 1, 7, 9, 0)  # A Monday, 09:00.
TODAY = FIXED_NOW.date().isoformat()
TOMORROW = (FIXED_NOW.date() + timedelta(days=1)).isoformat()
IN_TWO_DAYS = (FIXED_NOW.date() + timedelta(days=2)).isoformat()
YESTERDAY = (FIXED_NOW.date() - timedelta(days=1)).isoformat()

# (email, password) of the accounts seeded by the `database_path` fixture.
USER = ("user@smashgo.local", "UserTest123!")
OTHER_USER = ("user2@smashgo.local", "User2Test123!")
MANAGER = ("manager@smashgo.local", "ManagerTest123!")
ADMIN = ("admin@smashgo.local", "AdminTest123!")

USER_ID, OTHER_USER_ID, MANAGER_ID, ADMIN_ID = 1, 2, 3, 4
COURT_A, COURT_B = 1, 2
VERIFIED_ACCOUNT_ID = 1
MOCK_OTP = "123456"


def login(client, account=USER):
    email, secret = account
    response = client.post("/login", data={"email": email, "password": secret})
    assert response.status_code == 302


def query(database_path, sql, params=()):
    with sqlite3.connect(database_path) as connection:
        return connection.execute(sql, params).fetchall()


def execute(database_path, sql, params=()):
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(sql, params)
        return cursor.lastrowid


def add_booking(
    database_path,
    court_id=COURT_A,
    booking_date=TOMORROW,
    start="20:00",
    end="22:00",
    status="CONFIRMED",
    user_id=OTHER_USER_ID,
    amount=200000,
    hold_expires_at=None,
):
    return execute(
        database_path,
        """
        INSERT INTO Booking (
            UserID, CourtID, BookingDate, StartTime, EndTime, TotalAmount,
            DepositAmount, Status, HoldExpiresAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, court_id, booking_date, start, end, amount, amount, status, hold_expires_at),
    )


def add_payment(database_path, booking_id, amount, status="SUCCESS", refund_amount=None):
    return execute(
        database_path,
        """
        INSERT INTO Payment (
            BookingID, BankAccountID, Amount, PaymentMethod, TransactionCode,
            Status, RefundAmount, PaidAt
        ) VALUES (?, ?, ?, 'BANK_TRANSFER', ?, ?, ?, ?)
        """,
        (
            booking_id,
            VERIFIED_ACCOUNT_ID,
            amount,
            f"TEST-{booking_id}",
            status,
            refund_amount,
            FIXED_NOW.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )


def add_court_block(database_path, court_id=COURT_A, block_date=TOMORROW, start="10:00", end="12:00"):
    return execute(
        database_path,
        """
        INSERT INTO Court_Block (CourtID, BlockDate, StartTime, EndTime, Reason, CreatedBy)
        VALUES (?, ?, ?, ?, 'Bảo trì', ?)
        """,
        (court_id, block_date, start, end, MANAGER_ID),
    )


def add_court_request(database_path, court_name="Sân Mới Hoàng Mai", image_url="https://example.com/new.jpg"):
    request_id = execute(
        database_path,
        """
        INSERT INTO Court_Request (
            ManagerID, RequestType, CourtName, Location, Description,
            PricePerHour, OpenTime, CloseTime, Reason, Status
        ) VALUES (?, 'CREATE', ?, '9 Tam Trinh, Hoàng Mai, Hà Nội', 'Sân mới',
                  90000, '06:00', '22:00', 'Mở thêm cơ sở', 'PENDING')
        """,
        (MANAGER_ID, court_name),
    )
    execute(
        database_path,
        "INSERT INTO Court_Request_Image (RequestID, Url, SortOrder) VALUES (?, ?, 0)",
        (request_id, image_url),
    )
    return request_id
