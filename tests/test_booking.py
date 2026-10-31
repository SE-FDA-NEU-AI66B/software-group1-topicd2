import re
import threading
from datetime import timedelta

import pytest

from booking_service import BookingError, create_booking
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
    login,
)


def book(client, **overrides):
    payload = {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"}
    payload.update(overrides)
    return client.post("/api/bookings", json=payload)


def test_create_booking_holds_slot_for_ten_minutes(client):
    login(client)

    response = book(client)

    assert response.status_code == 201
    booking = response.get_json()
    assert booking["status"] == "PENDING"
    assert booking["totalAmount"] == 200000
    assert booking["holdExpiresAt"] == (FIXED_NOW + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")


def test_overlapping_booking_is_rejected_with_clear_message(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="22:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime="20:00", endTime="21:30")

    assert response.status_code == 409
    error = response.get_json()
    assert error["code"] == "SLOT_UNAVAILABLE"
    assert "20:00–22:00" in error["message"]


@pytest.mark.parametrize(
    ("start_time", "end_time", "message_part"),
    [
        ("08:00", "08:30", "ít nhất 1 giờ"),
        ("05:00", "07:00", "06:00 đến 22:00"),
        ("18:00", "19:30", "để trống 30 phút"),
    ],
)
def test_booking_rule_violations(client, database_path, start_time, end_time, message_part):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="22:00")
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime=start_time, endTime=end_time)

    assert response.status_code == 422
    assert response.get_json()["code"] == "BOOKING_RULE_VIOLATION"
    assert message_part in response.get_json()["message"]


def test_booking_in_the_past_is_rejected(client):
    login(client)

    response = book(client, bookingDate=FIXED_NOW.date().isoformat(), startTime="08:00", endTime="09:00")

    assert response.status_code == 422
    assert "đã qua" in response.get_json()["message"]


def test_contiguous_booking_is_allowed(client, database_path):
    add_booking(database_path, booking_date=TOMORROW, start="20:00", end="22:00")
    login(client)

    assert book(client, bookingDate=TOMORROW, startTime="18:00", endTime="20:00").status_code == 201


def test_third_active_booking_is_rejected(client):
    login(client)
    assert book(client, startTime="08:00", endTime="09:00").status_code == 201
    assert book(client, startTime="11:00", endTime="12:00").status_code == 201

    response = book(client, startTime="14:00", endTime="15:00")

    assert response.status_code == 409
    assert response.get_json()["code"] == "ACTIVE_BOOKING_LIMIT"


def test_expired_hold_releases_slot(database_path):
    create_booking(database_path, USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=FIXED_NOW)

    with pytest.raises(BookingError) as rejected:
        create_booking(database_path, OTHER_USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=FIXED_NOW)
    assert rejected.value.code == "SLOT_UNAVAILABLE"

    later = FIXED_NOW + timedelta(minutes=11)
    booking = create_booking(database_path, OTHER_USER_ID, COURT_A, IN_TWO_DAYS, "08:00", "10:00", now=later)
    assert booking["status"] == "PENDING"


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


def test_api_requires_logged_in_user(client):
    response = book(client)
    assert response.status_code == 401
    assert response.get_json()["code"] == "UNAUTHENTICATED"

    login(client, ADMIN)
    assert book(client).status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"courtId": COURT_A, "bookingDate": "not-a-date", "startTime": "08:00", "endTime": "10:00"},
        {"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:15", "endTime": "10:00"},
        {"courtId": "abc", "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    ],
)
def test_invalid_input_is_rejected(client, payload):
    login(client)

    response = client.post("/api/bookings", json=payload)

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_INPUT"


def test_unknown_court_is_not_found(client):
    login(client)
    assert book(client, courtId=999).status_code == 404


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
