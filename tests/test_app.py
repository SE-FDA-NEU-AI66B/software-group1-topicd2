import sqlite3

from app import create_app
from init_db import initialize_database


def test_courts_route_renders_database_records(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    seeded_count = initialize_database(database_path)
    assert seeded_count >= 10
    assert initialize_database(database_path) == seeded_count

    with sqlite3.connect(database_path) as connection:
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
    response = app.test_client().get("/courts")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert page.count('class="court-row"') >= 10
    assert "Sân được thêm trong test" in page