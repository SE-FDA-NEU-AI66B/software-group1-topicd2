import sqlite3

from support import TOMORROW

from app import create_app
from init_db import initialize_database


def test_courts_route_renders_database_records(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    seeded_count = initialize_database(database_path)
    assert seeded_count >= 10
    assert initialize_database(database_path) == seeded_count

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        assert tables == {
            "Users",
            "Court",
            "Court_Image",
            "Court_Block",
            "Booking",
            "BankAccount",
            "BankAccountVerification",
            "Payment",
            "Notification",
            "CheckIn",
            "Court_Report",
            "Court_Request",
            "Court_Request_Image",
        }

        manager_id = connection.execute(
            "SELECT UserID FROM Users WHERE Email = ?",
            ("walking-skeleton-manager@smashgo.local",),
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO Court (
                ManagerID, CourtName, Location, Description, PricePerHour,
                OpenTime, CloseTime, Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                manager_id,
                "Sân được thêm trong test",
                "Địa chỉ kiểm thử",
                "Bản ghi chỉ tồn tại trong SQLite test",
                75000,
                "07:00",
                "22:00",
                "ACTIVE",
            ),
        )

    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})
    client = app.test_client()
    root_response = client.get("/")
    response = client.get("/courts")
    page = response.get_data(as_text=True)

    assert root_response.status_code == 302
    assert root_response.location == "/courts"
    assert response.status_code == 200
    assert page.count('class="court-row"') >= 10
    assert "Sân được thêm trong test" in page

# Seed data of init_db.py (the demo database), checked here so the feature
# tests can run on the small fixture database from conftest.py.
def test_seed_contains_confirmed_demo_booking(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT CourtID, BookingDate, StartTime, EndTime, Status
            FROM Booking JOIN Users USING (UserID)
            WHERE Email = 'user2@smashgo.local'
            """
        ).fetchall()
    assert rows == [(1, TOMORROW, "20:00", "22:00", "CONFIRMED")]


def test_admin_request_seeds_are_idempotent_and_complete(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    initialize_database(database_path)
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        requests = connection.execute(
            """
            SELECT RequestType, CourtName, Location, OpenTime, CloseTime, PricePerHour
            FROM Court_Request WHERE CourtName LIKE 'SmashGo Demo Court Request %'
            """
        ).fetchall()
        images_count = connection.execute(
            """
            SELECT COUNT(*) FROM Court_Request_Image
            JOIN Court_Request USING (RequestID)
            WHERE CourtName LIKE 'SmashGo Demo Court Request %'
            """
        ).fetchone()[0]
    assert len(requests) == 2
    assert images_count == 2
    for request_type, court_name, location, open_time, close_time, price in requests:
        assert request_type == "CREATE"
        assert court_name and location
        assert open_time < close_time
        assert price > 0
