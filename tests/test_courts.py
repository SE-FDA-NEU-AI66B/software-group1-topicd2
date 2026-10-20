import sqlite3
from datetime import date, timedelta

import pytest

from app import create_app
from init_db import initialize_database

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# Task #95: Create an isolated seeded app for public court discovery tests.
@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    initialize_database(database_path)
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})
    return app.test_client()


# Task #95: Keep the existing root redirect and use /courts as the canonical listing route.
def test_root_redirects_to_canonical_courts_route(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.location == "/courts"


# Task #95: Render search filters and links to court details from the canonical listing page.
def test_court_listing_contains_filters_and_detail_links(client):
    response = client.get("/courts")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'name="location"' in page
    assert 'name="date"' in page
    assert 'name="startTime"' in page
    assert 'name="endTime"' in page
    assert "/courts/1" in page
    assert "Chi tiết sân" in page


# Task #95: Filter by location or court area name, treating SQL wildcard characters literally.
def test_court_listing_filters_by_location(client):
    response = client.get("/courts?location=C%E1%BA%A7u%20Gi%E1%BA%A5y")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "SmashGo Cầu Giấy 1" in page
    assert "SmashGo Đống Đa 1" not in page


# Task #95: Search the address fields as well as the area embedded in the court name.
def test_court_listing_filters_by_address(client):
    response = client.get(
        "/courts",
        query_string={"location": "Trần Thái Tông"},
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "SmashGo Cầu Giấy 1" in page
    assert "SmashGo Đống Đa 1" not in page


# Task #95: Treat a percent sign as a literal location character rather than a SQL wildcard.
def test_court_listing_escapes_location_wildcards(client):
    response = client.get("/courts", query_string={"location": "%"})

    assert response.status_code == 200
    assert "Không tìm thấy sân phù hợp" in response.get_data(as_text=True)


# Task #95: Filter courts by an available date/time and exclude occupied time intervals.
def test_court_listing_filters_by_date_and_availability(client):
    response = client.get(
        f"/courts?date={TOMORROW}&startTime=20%3A00&endTime=21%3A30"
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "SmashGo Cầu Giấy 1" not in page
    assert "SmashGo Cầu Giấy 2" in page
    assert f"date={TOMORROW}" in page
    assert "startTime=20:00" in page
    assert "endTime=21:30" in page


# Task #95: Expose the court-list filters through the public JSON endpoint as well as the HTML page.
def test_court_list_api_filters_location_and_time(client):
    response = client.get(
        f"/api/courts?location=C%E1%BA%A7u%20Gi%E1%BA%A5y&date={TOMORROW}"
        "&startTime=20%3A00&endTime=21%3A30"
    )

    assert response.status_code == 200
    courts = response.get_json()
    assert len(courts) == 1
    assert courts[0]["courtName"] == "SmashGo Cầu Giấy 2"
    assert courts[0]["images"][0]["sortOrder"] == 0


# Task #95: Show a clear validation error when date/time filter fields are incomplete.
def test_court_listing_shows_error_for_incomplete_time_filter(client):
    response = client.get(f"/courts?date={TOMORROW}&startTime=20%3A00")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "hợp lệ" in page
    assert 'role="alert"' in page


# Task #95: Render the active court details required before a user selects a time slot.
def test_court_detail_displays_price_location_condition_and_images(client):
    response = client.get("/courts/1")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "SmashGo Cầu Giấy 1" in page
    assert "102 Trần Thái Công" not in page
    assert "102 Trần Thái Tông Hà Nội" in page
    assert "90,000" in page
    assert "Sân thảm xanh tiêu chuẩn ánh sáng LED" in page
    assert "images.unsplash.com" in page


# Task #95: Do not expose disabled courts on public detail pages.
def test_disabled_court_detail_returns_not_found(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    initialize_database(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute("UPDATE Court SET Status = 'DISABLED' WHERE CourtID = 1")
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})

    response = app.test_client().get("/courts/1")

    assert response.status_code == 404
    assert "Không tìm thấy sân" in response.get_data(as_text=True)


# Task #95: Load dated availability with available, booked and unavailable states.
def test_availability_api_marks_overlapping_seeded_booking(client):
    response = client.get(
        f"/api/courts/1/availability?date={TOMORROW}"
    )

    assert response.status_code == 200
    result = response.get_json()
    slots = {slot["startTime"]: slot for slot in result["slots"]}
    assert slots["19:00"]["status"] == "AVAILABLE"
    assert slots["19:30"]["status"] == "BOOKED"
    assert slots["20:00"]["status"] == "BOOKED"
    assert slots["22:00"]["status"] == "AVAILABLE"
    assert all("endTime" in slot and "available" in slot for slot in result["slots"])


# Task #95: Mark short gaps beside existing bookings as unavailable under the contiguous-booking rule.
def test_availability_api_marks_short_gap_unavailable(client):
    response = client.get(f"/api/courts/1/availability?date={TOMORROW}")

    assert response.status_code == 200
    slots = {slot["startTime"]: slot for slot in response.get_json()["slots"]}
    assert slots["18:30"]["status"] == "UNAVAILABLE"
    assert slots["19:00"]["status"] == "AVAILABLE"


# Task #95: Return clear public API errors for invalid dates and inactive courts.
@pytest.mark.parametrize(
    ("url", "status", "code"),
    [
        ("/api/courts/1/availability?date=not-a-date", 400, "INVALID_AVAILABILITY_DATE"),
        ("/api/courts/9999/availability?date=2026-10-21", 404, "COURT_NOT_FOUND"),
    ],
)
def test_availability_api_reports_invalid_input_and_unknown_courts(
    client, url, status, code
):
    response = client.get(url)

    assert response.status_code == status
    assert response.get_json()["code"] == code


# Task #95: Render loading, empty and error UI hooks for asynchronous availability results.
def test_detail_page_exposes_availability_state_hooks(client):
    response = client.get("/courts/1")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="availability-state"' in page
    assert 'id="availability-slots"' in page
    assert "Đang tải lịch trống..." in page


# Task #95: Expose active court details through the documented public JSON endpoint.
def test_court_detail_api_returns_public_details_and_images(client):
    response = client.get("/api/courts/1")

    assert response.status_code == 200
    body = response.get_json()
    assert body["courtId"] == 1
    assert body["courtName"] == "SmashGo Cầu Giấy 1"
    assert body["pricePerHour"] == 90000
    assert body["images"][0]["url"].startswith("https://")


# Task #95: Ensure free slots navigate to /book with court, date and time prefilled.
def test_detail_page_slot_links_include_booking_selection(client):
    response = client.get("/courts/1")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-book-url="/book"' in page
    assert 'data-court-id="1"' in page
    assert 'court_detail.js' in page
