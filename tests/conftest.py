"""Shared fixtures: a temporary seeded database, a test client, a frozen
clock and a fake bank gateway.

No test needs a running server, the real database in instance/, a .env
file, the data/ folder or the real current time.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from support import (
    ADMIN,
    COURT_A,
    COURT_B,
    FIXED_NOW,
    MANAGER,
    MANAGER_ID,
    MOCK_OTP,
    OTHER_USER,
    USER,
    USER_ID,
)
from werkzeug.security import generate_password_hash

import bank_gateway
import clock
from app import create_app

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"

# Hash once per run: password hashing is deliberately slow.
SEED_USERS = [
    ("Người chơi Test", USER, "USER"),
    ("Người chơi Hai", OTHER_USER, "USER"),
    ("Chủ sân Test", MANAGER, "MANAGER"),
    ("Quản trị Test", ADMIN, "ADMIN"),
]
SEED_USER_ROWS = [
    (full_name, email, generate_password_hash(secret), role)
    for full_name, (email, secret), role in SEED_USERS
]


class FrozenClock:
    """Replaces clock.now; tests move time with set() or advance()."""

    def __init__(self, current: datetime):
        self.current = current

    def now(self) -> datetime:
        return self.current

    def set(self, value: datetime) -> None:
        self.current = value

    def advance(self, **delta) -> None:
        self.current += timedelta(**delta)


class FakeGateway:
    """Stands in for bank_gateway: fixed OTP, no outside calls, records requests."""

    def __init__(self):
        self.otp = MOCK_OTP
        self.fail_charges = False
        self.sent_otps: list[tuple[str, str]] = []
        self.charges: list[tuple[str, str, float]] = []

    def send_otp(self, bank_name: str, account_number: str) -> str:
        self.sent_otps.append((bank_name, account_number))
        return self.otp

    def charge(self, bank_name: str, account_number: str, amount: float) -> str | None:
        self.charges.append((bank_name, account_number, amount))
        if self.fail_charges:
            return None
        return f"FAKE-{len(self.charges):04d}"


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    fake = FrozenClock(FIXED_NOW)
    monkeypatch.setattr(clock, "now", fake.now)
    return fake


@pytest.fixture(autouse=True)
def fake_gateway(monkeypatch):
    fake = FakeGateway()
    monkeypatch.setattr(bank_gateway, "send_otp", fake.send_otp)
    monkeypatch.setattr(bank_gateway, "charge", fake.charge)
    return fake


def seed_minimal(connection: sqlite3.Connection) -> None:
    connection.executemany(
        "INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES (?, ?, ?, ?)",
        SEED_USER_ROWS,
    )
    connection.executemany(
        """
        INSERT INTO Court (
            CourtID, ManagerID, CourtName, Location, Description, PricePerHour,
            OpenTime, CloseTime, Status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """,
        [
            (
                COURT_A,
                MANAGER_ID,
                "Sân Cầu Giấy A",
                "12 Trần Thái Tông, Cầu Giấy, Hà Nội",
                "Thảm xanh, đèn LED",
                100000,
                "06:00",
                "22:00",
            ),
            (
                COURT_B,
                MANAGER_ID,
                "Sân Đống Đa B",
                "5 Tây Sơn, Đống Đa, Hà Nội",
                "Sân rộng, có chỗ để xe",
                80000,
                "07:00",
                "21:00",
            ),
        ],
    )
    # Court A's images are inserted out of order to check ordering by SortOrder.
    connection.executemany(
        "INSERT INTO Court_Image (CourtID, Url, SortOrder) VALUES (?, ?, ?)",
        [
            (COURT_A, "https://example.com/court-a-2.jpg", 1),
            (COURT_A, "https://example.com/court-a-1.jpg", 0),
            (COURT_B, "https://example.com/court-b-1.jpg", 0),
        ],
    )
    connection.execute(
        """
        INSERT INTO BankAccount (
            UserID, BankName, AccountNumber, AccountHolderName, IsVerified, VerifiedAt
        ) VALUES (?, 'Vietcombank', '0123456789', 'NGUOI CHOI TEST', 1, ?)
        """,
        (USER_ID, (FIXED_NOW - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")),
    )


@pytest.fixture
def database_path(tmp_path):
    """A fresh SQLite file built from schema.sql with the minimal seed:
    2 Users, 1 Manager, 1 Admin, 2 ACTIVE courts and 1 verified bank account."""
    path = tmp_path / "smashgo-test.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        seed_minimal(connection)
    return path


@pytest.fixture
def app(database_path):
    return create_app(
        {"TESTING": True, "DATABASE_PATH": str(database_path), "SECRET_KEY": "test-only"}
    )


@pytest.fixture
def client(app):
    return app.test_client()
