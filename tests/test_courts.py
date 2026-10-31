import pytest
from support import COURT_A, TOMORROW, add_booking, execute


# Task #95: Give court A a confirmed 20:00-22:00 booking tomorrow.
@pytest.fixture
def booked_client(client, database_path):
    add_booking(database_path, COURT_A, TOMORROW, "20:00", "22:00", "CONFIRMED")
    return client


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
    response = client.get("/courts", query_string={"location": "Cầu Giấy"})
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" in page
    assert "Sân Đống Đa B" not in page


# Task #95: Search the address fields as well as the area embedded in the court name.
def test_court_listing_filters_by_address(client):
    response = client.get("/courts", query_string={"location": "Trần Thái Tông"})
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" in page
    assert "Sân Đống Đa B" not in page


# Task #95: Treat a percent sign as a literal location character rather than a SQL wildcard.
def test_court_listing_escapes_location_wildcards(client):
    response = client.get("/courts", query_string={"location": "%"})

    assert response.status_code == 200
    assert "Không tìm thấy sân phù hợp" in response.get_data(as_text=True)


# Task #95: Filter courts by an available date/time and exclude occupied time intervals.
def test_court_listing_filters_by_date_and_availability(booked_client):
    response = booked_client.get(f"/courts?date={TOMORROW}&startTime=19%3A00&endTime=20%3A30")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" not in page
    assert "Sân Đống Đa B" in page
    assert f"date={TOMORROW}" in page
    assert "startTime=19:00" in page
    assert "endTime=20:30" in page


# Task #95: Expose the court-list filters through the public JSON endpoint as well as the HTML page.
def test_court_list_api_filters_location_and_time(booked_client):
    response = booked_client.get(
        "/api/courts",
        query_string={"location": "Hà Nội", "date": TOMORROW, "startTime": "19:00", "endTime": "20:30"},
    )

    assert response.status_code == 200
    courts = response.get_json()
    assert len(courts) == 1
    assert courts[0]["courtName"] == "Sân Đống Đa B"
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
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" in page
    assert "12 Trần Thái Tông, Cầu Giấy, Hà Nội" in page
    assert "100,000" in page
    assert "Thảm xanh, đèn LED" in page
    assert "https://example.com/court-a-1.jpg" in page


# Task #95: Do not expose disabled courts on public detail pages.
def test_disabled_court_detail_returns_not_found(client, database_path):
    execute(database_path, "UPDATE Court SET Status = 'DISABLED' WHERE CourtID = ?", (COURT_A,))

    response = client.get(f"/courts/{COURT_A}")

    assert response.status_code == 404
    assert "Không tìm thấy sân" in response.get_data(as_text=True)


# Task #95: Load dated availability with available, booked and unavailable states.
def test_availability_api_marks_overlapping_booking(booked_client):
    response = booked_client.get(f"/api/courts/{COURT_A}/availability?date={TOMORROW}")

    assert response.status_code == 200
    result = response.get_json()
    slots = {slot["startTime"]: slot for slot in result["slots"]}
    assert slots["19:00"]["status"] == "AVAILABLE"
    assert slots["19:30"]["status"] == "BOOKED"
    assert slots["20:00"]["status"] == "BOOKED"
    assert slots["21:00"]["status"] == "BOOKED"
    assert all("endTime" in slot and "available" in slot for slot in result["slots"])


# Task #95: Mark short gaps beside existing bookings as unavailable under the contiguous-booking rule.
def test_availability_api_marks_short_gap_unavailable(booked_client):
    response = booked_client.get(f"/api/courts/{COURT_A}/availability?date={TOMORROW}")

    assert response.status_code == 200
    slots = {slot["startTime"]: slot for slot in response.get_json()["slots"]}
    assert slots["18:30"]["status"] == "UNAVAILABLE"
    assert slots["19:00"]["status"] == "AVAILABLE"


# Task #95: Return clear public API errors for invalid dates and inactive courts.
@pytest.mark.parametrize(
    ("url", "status", "code"),
    [
        ("/api/courts/1/availability?date=not-a-date", 400, "INVALID_AVAILABILITY_DATE"),
        (f"/api/courts/9999/availability?date={TOMORROW}", 404, "COURT_NOT_FOUND"),
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
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="availability-state"' in page
    assert 'id="availability-slots"' in page
    assert "Đang tải lịch trống..." in page


# Task #95: Expose active court details through the documented public JSON endpoint.
def test_court_detail_api_returns_public_details_and_images(client):
    response = client.get(f"/api/courts/{COURT_A}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["courtId"] == COURT_A
    assert body["courtName"] == "Sân Cầu Giấy A"
    assert body["pricePerHour"] == 100000
    assert body["images"][0]["url"] == "https://example.com/court-a-1.jpg"


# Task #95: Ensure free slots navigate to /book with court, date and time prefilled.
def test_detail_page_slot_links_include_booking_selection(client):
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-book-url="/book"' in page
    assert f'data-court-id="{COURT_A}"' in page
    assert 'court_detail.js' in page
