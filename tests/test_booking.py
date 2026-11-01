import re
import sqlite3
import threading
from datetime import timedelta

import pytest
from support import (
    ADMIN,
    COURT_A,
    COURT_B,
    FIXED_NOW,
    IN_TWO_DAYS,
    MANAGER,
    OTHER_USER_ID,
    TOMORROW,
    USER,
    USER_ID,
    add_booking,
    add_court_block,
    login,
)

from booking_service import BookingError, create_booking


def book(client, **overrides):
    payload = {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"}
    payload.update(overrides)
    return client.post("/api/bookings", json=payload)


# TC-12: A free slot creates a pending booking with a ten-minute hold.
def test_tc12_create_booking_holds_slot_for_ten_minutes(client):
    login(client)

    response = book(client)

    assert response.status_code == 201
    booking = response.get_json()
    assert booking["status"] == "PENDING"
    assert booking["totalAmount"] == 200000
    assert booking["holdExpiresAt"] == (FIXED_NOW + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")


# TC-13: A 30-minute booking violates the one-hour minimum.
def test_tc13_booking_of_30_minutes_is_rejected_by_minimum_duration(client):
    login(client)

    response = book(client, startTime="08:00", endTime="08:30")

    assert response.status_code == 422
    assert response.get_json()["code"] == "BOOKING_RULE_VIOLATION"


# TC-14: The exact one-hour minimum is allowed.
def test_tc14_booking_of_60_minutes_is_allowed(client):
    login(client)

    response = book(client, startTime="08:00", endTime="09:00")

    assert response.status_code == 201


# TC-15: A 90-minute booking just above the one-hour minimum is allowed.
def test_tc15_booking_of_90_minutes_is_allowed(client):
    login(client)

    response = book(client, startTime="08:00", endTime="09:30")

    assert response.status_code == 201


# TC-16: Back-to-back bookings with no gap are allowed.
def test_tc16_booking_adjacent_to_an_existing_booking_is_allowed(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="21:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="19:00", endTime="20:00")

    assert response.status_code == 201


# TC-17: A 30-minute gap is below BR2's one-hour minimum.
def test_tc17_booking_with_30_minute_gap_is_rejected(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="21:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="18:30", endTime="19:30")

    assert response.status_code == 422
    assert response.get_json()["code"] == "BOOKING_RULE_VIOLATION"


# TC-18: A 60-minute gap meets BR2's minimum and is allowed.
def test_tc18_booking_with_60_minute_gap_is_allowed(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="21:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="18:00", endTime="19:00")

    assert response.status_code == 201


# TC-56: Court blocks reject overlap but do not impose BR2 gaps before or after the block.
def test_tc56_booking_can_be_near_a_court_block(client, database_path):
    add_court_block(database_path, COURT_A, TOMORROW, "10:00", "12:00")
    login(client)

    before_block = book(
        client,
        bookingDate=TOMORROW,
        startTime="08:00",
        endTime="09:30",
    )
    after_block = book(
        client,
        bookingDate=TOMORROW,
        startTime="12:30",
        endTime="13:30",
    )

    assert before_block.status_code == 201
    assert after_block.status_code == 201


# TC-19: Unexpired pending holds occupy their slot; expired and cancelled bookings release it.
@pytest.mark.parametrize(
    ("status", "hold_expires_at", "expected_status"),
    [
        (
            "PENDING",
            (FIXED_NOW + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            409,
        ),
        ("EXPIRED", None, 201),
        ("CANCELLED", None, 201),
    ],
    ids=["pending-hold-occupies", "expired-releases", "cancelled-releases"],
)
def test_tc19_booking_status_controls_slot_occupancy(
    client, database_path, status, hold_expires_at, expected_status
):
    add_booking(
        database_path,
        booking_date=TOMORROW,
        start="20:00",
        end="21:00",
        status=status,
        hold_expires_at=hold_expires_at,
    )
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="20:00", endTime="21:00")

    assert response.status_code == expected_status
    if expected_status == 409:
        assert response.get_json()["code"] == "SLOT_UNAVAILABLE"


# TC-20: The first and second active bookings are allowed.
def test_tc20_first_and_second_active_bookings_are_allowed(client):
    login(client)

    assert book(client, startTime="08:00", endTime="09:00").status_code == 201
    assert book(client, startTime="11:00", endTime="12:00").status_code == 201


# TC-21: A third active booking is rejected; expired and cancelled bookings do not count.
def test_tc21_active_booking_limit_and_inactive_statuses(client, database_path):
    first_id = add_booking(
        database_path, booking_date=IN_TWO_DAYS, start="08:00", end="09:00", user_id=USER_ID
    )
    second_id = add_booking(
        database_path, booking_date=IN_TWO_DAYS, start="11:00", end="12:00", user_id=USER_ID
    )
    login(client)

    response = book(client, startTime="14:00", endTime="15:00")
    assert response.status_code == 409
    assert response.get_json()["code"] == "ACTIVE_BOOKING_LIMIT"

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE Booking SET Status = ? WHERE BookingID = ?",
            ("CANCELLED", first_id),
        )
        connection.execute(
            "UPDATE Booking SET Status = ? WHERE BookingID = ?",
            ("EXPIRED", second_id),
        )

    assert book(client, startTime="14:00", endTime="15:00").status_code == 201


# TC-22: Authentication, missing input, malformed input, and unknown courts return their API errors.
@pytest.mark.parametrize(
    ("account", "payload", "expected_status", "expected_code"),
    [
        (None, {"courtId": COURT_A}, 401, "UNAUTHENTICATED"),
        (USER, {}, 400, "INVALID_INPUT"),
        (
            USER,
            {"courtId": COURT_A, "bookingDate": "not-a-date", "startTime": "08:00", "endTime": "10:00"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:15", "endTime": "10:00"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:xx"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "08:59"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "09:01"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": "abc", "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
            400,
            "INVALID_INPUT",
        ),
        (
            USER,
            {"courtId": 999, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
            404,
            "COURT_NOT_FOUND",
        ),
        (
            ADMIN,
            {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
            403,
            "FORBIDDEN",
        ),
    ],
    ids=[
        "guest",
        "missing-input",
        "invalid-date",
        "off-step-start",
        "invalid-end-time",
        "end-before-step",
        "end-after-step",
        "invalid-court-id",
        "unknown-court",
        "non-player",
    ],
)
def test_tc22_booking_api_validates_authentication_and_input(
    client, account, payload, expected_status, expected_code
):
    if account is not None:
        login(client, account)

    response = client.post("/api/bookings", json=payload)

    assert response.status_code == expected_status
    assert response.get_json()["code"] == expected_code


# TC-23: A booking that partially overlaps an occupied slot is rejected.
def test_tc23_partial_overlap_is_rejected_with_clear_message(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="22:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="19:30", endTime="20:30")

    assert response.status_code == 409
    error = response.get_json()
    assert error["code"] == "SLOT_UNAVAILABLE"
    assert "20:00–22:00" in error["message"]


# TC-24: A new booking may start exactly when an existing booking ends.
def test_tc24_contiguous_booking_is_allowed(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="22:00")
    login(client)

    assert book(client, bookingDate=TOMORROW, startTime="19:00", endTime="20:00").status_code == 201


# TC-25: Two independent booking requests for the same court and slot have one winner.
def test_simultaneous_requests_for_same_slot_have_one_winner(database_path):
    user_ids = [USER_ID, OTHER_USER_ID]
    barrier = threading.Barrier(len(user_ids))
    results = []

    def attempt(current_user_id):
        barrier.wait()
        try:
            create_booking(database_path, current_user_id, COURT_B, IN_TWO_DAYS, "15:00", "17:00")
            results.append("CREATED")
        except BookingError as error:
            results.append(error.code)

    threads = [threading.Thread(target=attempt, args=(uid,)) for uid in user_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(results) == ["CREATED", "SLOT_UNAVAILABLE"]


# TC-26: The repository rejects a booking whose end time is not after its start time.
def test_tc26_repository_rejects_booking_end_not_after_start(database_path):
    with sqlite3.connect(database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            connection.execute(
                """
                INSERT INTO Booking (
                    UserID, CourtID, BookingDate, StartTime, EndTime,
                    TotalAmount, DepositAmount, Status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (USER_ID, COURT_A, IN_TWO_DAYS, "09:00", "08:00", 100000, 100000, "PENDING"),
            )


def test_booking_in_the_past_is_rejected(client):
    login(client)

    response = book(client, bookingDate=FIXED_NOW.date().isoformat(), startTime="08:00", endTime="09:00")

    assert response.status_code == 422
    assert "đã qua" in response.get_json()["message"]


# TC-19 also verifies that a pending hold releases its slot after expiring.
def test_expired_hold_releases_slot(database_path):
    create_booking(database_path, USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=FIXED_NOW)

    with pytest.raises(BookingError) as rejected:
        create_booking(database_path, OTHER_USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=FIXED_NOW)
    assert rejected.value.code == "SLOT_UNAVAILABLE"

    later = FIXED_NOW + timedelta(minutes=11)
    booking = create_booking(database_path, OTHER_USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=later)
    assert booking["status"] == "PENDING"


def test_guest_sees_book_page_with_selection_prefilled(client):
    response = client.get(f"/book?courtId={COURT_B}&date={TOMORROW}&startTime=18:00&endTime=20:00")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'data-authenticated="false"' in page
    assert f'value="{TOMORROW}"' in page
    assert 'data-initial="18:00"' in page
    assert 'data-initial="20:00"' in page
    assert 'data-availability-url="/api/courts/0/availability"' in page
    assert 'id="booking-schedule-grid"' in page
    assert 'data-name="Sân Cầu Giấy A"' in page
    assert "Chọn ô còn trống" in page
    selected_options = re.findall(r'<option value="(\d+)"[^>]*\bselected\b', page)
    assert selected_options == [str(COURT_B)]


def test_login_returns_user_to_book_with_selection(client):
    next_url = f"/book?courtId={COURT_B}&date={TOMORROW}&startTime=18:00&endTime=20:00&restored=1"
    email, secret = USER

    response = client.post("/login", data={"email": email, "password": secret, "next": next_url})
    assert response.status_code == 302
    assert response.location == next_url

    page = client.get(next_url).get_data(as_text=True)
    assert 'data-authenticated="true"' in page
    assert "Lựa chọn của bạn đã được giữ nguyên" in page


def test_manager_cannot_open_book_page(client):
    login(client, MANAGER)
    assert client.get("/book").status_code == 403
