from datetime import datetime
from itertools import pairwise

import pytest
from support import COURT_A, COURT_B, TOMORROW, add_booking, add_court_block, execute


# Task #95: Give court A a confirmed 20:00-22:00 booking tomorrow.
@pytest.fixture
def booked_client(client, database_path):
    add_booking(database_path, COURT_A, TOMORROW, "20:00", "22:00", "CONFIRMED")
    return client


def add_court(database_path, name, status, location="9 Kim Mã, Ba Đình, Hà Nội"):
    return execute(
        database_path,
        """
        INSERT INTO Court (
            ManagerID, CourtName, Location, Description, PricePerHour,
            OpenTime, CloseTime, Status
        ) VALUES (3, ?, ?, 'Sân kiểm thử', 90000, '06:00', '22:00', ?)
        """,
        (name, location, status),
    )


def list_courts(client, **filters):
    return client.get("/api/courts", query_string=filters)


def availability(client, court_id=COURT_A, booking_date=TOMORROW):
    return client.get(f"/api/courts/{court_id}/availability", query_string={"date": booking_date})


def slots_by_start(response):
    return {slot["startTime"]: slot for slot in response.get_json()["slots"]}


# ---------------------------------------------------------------------------
# US-01 - View available badminton courts: GET /api/courts (TC-01 to TC-04)
# ---------------------------------------------------------------------------


# TC-01: A date + time filter lists free ACTIVE courts only; a court with an
# overlapping booking and DISABLED / MAINTENANCE courts are left out.
def test_tc01_time_filter_lists_only_free_active_courts(booked_client, database_path):
    add_court(database_path, "Sân Đang Tắt", "DISABLED")
    add_court(database_path, "Sân Đang Bảo Trì", "MAINTENANCE")

    response = list_courts(booked_client, date=TOMORROW, startTime="20:00", endTime="21:00")

    assert response.status_code == 200
    assert [court["courtName"] for court in response.get_json()] == ["Sân Đống Đa B"]


# TC-01: Without filters the list holds every ACTIVE court and no inactive one.
def test_tc01_list_without_filters_hides_inactive_courts(client, database_path):
    add_court(database_path, "Sân Đang Tắt", "DISABLED")
    add_court(database_path, "Sân Đang Bảo Trì", "MAINTENANCE")

    response = list_courts(client)

    assert response.status_code == 200
    assert [court["courtId"] for court in response.get_json()] == [COURT_A, COURT_B]


# TC-02: Date and both times must be given together, on 30-minute steps.
@pytest.mark.parametrize(
    "filters",
    [
        {"startTime": "19:00", "endTime": "20:00"},
        {"date": TOMORROW, "endTime": "20:00"},
        {"date": TOMORROW, "startTime": "19:00"},
        {"date": TOMORROW, "startTime": "19:15", "endTime": "20:15"},
        {"date": TOMORROW, "startTime": "19:00", "endTime": "20:10"},
        {"date": "2030-13-40", "startTime": "19:00", "endTime": "20:00"},
    ],
    ids=["no-date", "no-start", "no-end", "start-off-step", "end-off-step", "bad-date"],
)
def test_tc02_incomplete_or_off_step_filter_is_rejected(client, filters):
    response = list_courts(client, **filters)

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_COURT_FILTER"


# TC-03: Boundary (on the limit) - a 60-minute window is the shortest valid filter.
def test_tc03_sixty_minute_window_is_accepted(client):
    response = list_courts(client, date=TOMORROW, startTime="19:00", endTime="20:00")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


# TC-04: Boundary (just below) - a 30-minute window is shorter than one booking.
def test_tc04_thirty_minute_window_is_rejected(client):
    response = list_courts(client, date=TOMORROW, startTime="19:00", endTime="19:30")

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_COURT_FILTER"


# TC-01 (page): Task #95: Filter courts by an available date/time and exclude occupied time intervals.
def test_court_listing_filters_by_date_and_availability(booked_client):
    response = booked_client.get(f"/courts?date={TOMORROW}&startTime=19%3A00&endTime=20%3A30")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" not in page
    assert "Sân Đống Đa B" in page
    assert f"date={TOMORROW}" in page
    assert "startTime=19:00" in page
    assert "endTime=20:30" in page


# TC-01: Task #95: Expose the court-list filters through the public JSON endpoint as well as the HTML page.
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


# TC-02 (page): Task #95: Show a clear validation error when date/time filter fields are incomplete.
def test_court_listing_shows_error_for_incomplete_time_filter(client):
    response = client.get(f"/courts?date={TOMORROW}&startTime=20%3A00")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "hợp lệ" in page
    assert 'role="alert"' in page


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


# ---------------------------------------------------------------------------
# US-02 - View detailed court information: GET /api/courts/{courtId} (TC-05 to TC-07)
# ---------------------------------------------------------------------------


# TC-05: The detail holds price, address, description and all images in SortOrder.
def test_tc05_court_detail_returns_price_location_description_and_ordered_images(client):
    response = client.get(f"/api/courts/{COURT_A}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["courtId"] == COURT_A
    assert body["courtName"] == "Sân Cầu Giấy A"
    assert body["pricePerHour"] == 100000
    assert body["location"] == "12 Trần Thái Tông, Cầu Giấy, Hà Nội"
    assert body["description"] == "Thảm xanh, đèn LED"
    assert (body["openTime"], body["closeTime"]) == ("06:00", "22:00")
    assert body["images"] == [
        {"url": "https://example.com/court-a-1.jpg", "sortOrder": 0},
        {"url": "https://example.com/court-a-2.jpg", "sortOrder": 1},
    ]


# TC-06: A court id that does not exist gives 404 COURT_NOT_FOUND.
def test_tc06_unknown_court_is_not_found(client):
    response = client.get("/api/courts/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "COURT_NOT_FOUND"


# TC-07: A court that is not ACTIVE is hidden from the public detail.
@pytest.mark.parametrize("status", ["DISABLED", "MAINTENANCE"])
def test_tc07_inactive_court_is_not_found(client, database_path, status):
    execute(database_path, "UPDATE Court SET Status = ? WHERE CourtID = ?", (status, COURT_A))

    response = client.get(f"/api/courts/{COURT_A}")

    assert response.status_code == 404
    assert response.get_json()["code"] == "COURT_NOT_FOUND"


# TC-05 (page): Task #95: Render the active court details required before a user selects a time slot.
def test_court_detail_displays_price_location_condition_and_images(client):
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sân Cầu Giấy A" in page
    assert "12 Trần Thái Tông, Cầu Giấy, Hà Nội" in page
    assert "100,000" in page
    assert "Thảm xanh, đèn LED" in page
    assert "https://example.com/court-a-1.jpg" in page


# TC-07 (page): Task #95: Do not expose disabled courts on public detail pages.
def test_disabled_court_detail_returns_not_found(client, database_path):
    execute(database_path, "UPDATE Court SET Status = 'DISABLED' WHERE CourtID = ?", (COURT_A,))

    response = client.get(f"/courts/{COURT_A}")

    assert response.status_code == 404
    assert "Không tìm thấy sân" in response.get_data(as_text=True)


# ---------------------------------------------------------------------------
# US-03 - View available time slots: GET /api/courts/{courtId}/availability (TC-08 to TC-11)
# ---------------------------------------------------------------------------


# TC-08: Slots last 1 hour, start every 30 minutes, and run from OpenTime.
def test_tc08_slots_are_one_hour_on_thirty_minute_steps(client):
    response = availability(client)

    assert response.status_code == 200
    slots = response.get_json()["slots"]
    starts = [datetime.strptime(slot["startTime"], "%H:%M") for slot in slots]
    ends = [datetime.strptime(slot["endTime"], "%H:%M") for slot in slots]
    assert slots[0]["startTime"] == "06:00"
    assert all((end - start).seconds == 3600 for start, end in zip(starts, ends))
    assert all((after - before).seconds == 1800 for before, after in pairwise(starts))
    assert all(slot["status"] == "AVAILABLE" and slot["available"] for slot in slots)


# TC-09: Overlaps with bookings and blocks are BOOKED; BR2 gaps apply only to bookings.
def test_tc09_booked_and_blocked_slots_are_not_available(client, database_path):
    add_booking(database_path, COURT_A, TOMORROW, "20:00", "22:00", "CONFIRMED")
    add_court_block(database_path, COURT_A, TOMORROW, "10:00", "12:00")

    slots = slots_by_start(availability(client))

    for start in (
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",
        "19:30",
        "20:00",
        "20:30",
        "21:00",
    ):
        assert slots[start]["status"] == "BOOKED", start
        assert slots[start]["available"] is False
    assert slots["12:00"]["status"] == "AVAILABLE"
    assert slots["12:30"]["status"] == "AVAILABLE"
    assert slots["12:30"]["available"] is True
    assert slots["19:00"]["status"] == "AVAILABLE"
    assert slots["18:30"]["status"] == "UNAVAILABLE"
    assert slots["18:30"]["available"] is False


# TC-10: A missing or invalid date gives 400 INVALID_AVAILABILITY_DATE.
@pytest.mark.parametrize("query", ["", "?date=", "?date=not-a-date", "?date=2030-02-30"])
def test_tc10_missing_or_invalid_date_is_rejected(client, query):
    response = client.get(f"/api/courts/{COURT_A}/availability{query}")

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_AVAILABILITY_DATE"


# TC-11: Boundary on both sides of CloseTime - the slot that ends exactly at
# CloseTime is offered; one that would run 30 minutes past it is not.
@pytest.mark.parametrize(
    ("court_id", "last_start", "past_close_start"),
    [(COURT_A, "21:00", "21:30"), (COURT_B, "20:00", "20:30")],
)
def test_tc11_last_slot_ends_exactly_at_close_time(client, court_id, last_start, past_close_start):
    slots = slots_by_start(availability(client, court_id))

    assert last_start in slots
    assert past_close_start not in slots
    assert max(slot["endTime"] for slot in slots.values()) == {COURT_A: "22:00", COURT_B: "21:00"}[court_id]


# TC-53: Requesting availability for a court that does not exist returns 404.
def test_tc53_availability_for_unknown_court_returns_not_found(client):
    response = client.get(f"/api/courts/9999/availability?date={TOMORROW}")

    assert response.status_code == 404
    assert response.get_json()["code"] == "COURT_NOT_FOUND"


# TC-09: Task #95: Load dated availability with available, booked and unavailable states.
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


# TC-09 (BR2): Task #95: Mark short gaps beside existing bookings as unavailable under the contiguous-booking rule.
def test_availability_api_marks_short_gap_unavailable(booked_client):
    response = booked_client.get(f"/api/courts/{COURT_A}/availability?date={TOMORROW}")

    assert response.status_code == 200
    slots = {slot["startTime"]: slot for slot in response.get_json()["slots"]}
    assert slots["18:30"]["status"] == "UNAVAILABLE"
    assert slots["19:00"]["status"] == "AVAILABLE"


# TC-10: Task #95: Return clear public API errors for invalid dates and inactive courts.
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


# ---------------------------------------------------------------------------
# Routes (status code only)
# ---------------------------------------------------------------------------


# TC-01 (route): the public court list page opens.
def test_route_courts_page_returns_ok(client):
    assert client.get("/courts").status_code == 200


# TC-05 (route): the court detail page opens for an active court.
def test_route_court_detail_page_returns_ok(client):
    assert client.get(f"/courts/{COURT_A}").status_code == 200


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


# Task #95: Render loading, empty and error UI hooks for asynchronous availability results.
def test_detail_page_exposes_availability_state_hooks(client):
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="availability-state"' in page
    assert 'id="availability-slots"' in page
    assert "Đang tải lịch trống..." in page


# Task #95: Ensure free slots navigate to /book with court, date and time prefilled.
def test_detail_page_slot_links_include_booking_selection(client):
    response = client.get(f"/courts/{COURT_A}")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-book-url="/book"' in page
    assert f'data-court-id="{COURT_A}"' in page
    assert 'court_detail.js' in page
