import re
import sqlite3
import threading
from datetime import date, datetime, timedelta

import pytest

from app import create_app
from booking_service import BookingError, create_booking
from init_db import initialize_database

TOMORROW = (date.today() + timedelta(days=1)).isoformat()
IN_TWO_DAYS = (date.today() + timedelta(days=2)).isoformat()


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "smashgo.sqlite3"
    initialize_database(path)
    return path


@pytest.fixture
def app(database_path):
    return create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})


def user_id(database_path, email):
    with sqlite3.connect(database_path) as connection:
        return connection.execute("SELECT UserID FROM Users WHERE Email = ?", (email,)).fetchone()[0]


DEMO_USER = ("user@smashgo.local", "UserTest123!")


def login(client, account=DEMO_USER):
    email, secret = account
    response = client.post("/login", data={"email": email, "password": secret})
    assert response.status_code == 302


def book(client, **overrides):
    payload = {"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"}
    payload.update(overrides)
    return client.post("/api/bookings", json=payload)


def test_seed_contains_confirmed_demo_booking(database_path):
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


def test_create_booking_holds_slot_for_ten_minutes(app):
    client = app.test_client()
    login(client)

    response = book(client)

    assert response.status_code == 201
    booking = response.get_json()
    assert booking["status"] == "PENDING"
    assert booking["totalAmount"] == 180000
    hold = datetime.fromisoformat(booking["holdExpiresAt"])
    assert timedelta(minutes=9) < hold - datetime.now() <= timedelta(minutes=10)


def test_overlapping_seeded_booking_is_rejected_with_clear_message(app):
    client = app.test_client()
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
        ("05:00", "07:00", "06:00 đến 23:00"),
        ("18:00", "19:30", "để trống 30 phút"),
    ],
)
def test_booking_rule_violations(app, start_time, end_time, message_part):
    client = app.test_client()
    login(client)

    response = book(client, bookingDate=TOMORROW, startTime=start_time, endTime=end_time)

    assert response.status_code == 422
    assert response.get_json()["code"] == "BOOKING_RULE_VIOLATION"
    assert message_part in response.get_json()["message"]


def test_contiguous_booking_is_allowed(app):
    client = app.test_client()
    login(client)

    assert book(client, bookingDate=TOMORROW, startTime="18:00", endTime="20:00").status_code == 201


def test_third_active_booking_is_rejected(app):
    client = app.test_client()
    # A fresh account: the seeded demo user already has an upcoming booking.
    registered = client.post(
        "/register",
        data={"full_name": "Limit Tester", "email": "limit@smashgo.local", "password": DEMO_USER[1]},
    )
    assert registered.status_code == 302
    assert book(client, startTime="08:00", endTime="09:00").status_code == 201
    assert book(client, startTime="11:00", endTime="12:00").status_code == 201

    response = book(client, startTime="14:00", endTime="15:00")

    assert response.status_code == 409
    assert response.get_json()["code"] == "ACTIVE_BOOKING_LIMIT"


def test_expired_hold_releases_slot(database_path):
    first_user = user_id(database_path, "user@smashgo.local")
    second_user = user_id(database_path, "user2@smashgo.local")
    now = datetime.now()
    create_booking(database_path, first_user, 1, IN_TWO_DAYS, "08:00", "10:00", now=now)

    with pytest.raises(BookingError) as rejected:
        create_booking(database_path, second_user, 1, IN_TWO_DAYS, "08:00", "10:00", now=now)
    assert rejected.value.code == "SLOT_UNAVAILABLE"

    later = now + timedelta(minutes=11)
    booking = create_booking(database_path, second_user, 1, IN_TWO_DAYS, "08:00", "10:00", now=later)
    assert booking["status"] == "PENDING"


def test_simultaneous_requests_for_same_slot_have_one_winner(database_path):
    user_ids = [
        user_id(database_path, "user@smashgo.local"),
        user_id(database_path, "user2@smashgo.local"),
    ]
    barrier = threading.Barrier(len(user_ids))
    results = []

    def attempt(current_user_id):
        barrier.wait()
        try:
            create_booking(database_path, current_user_id, 2, IN_TWO_DAYS, "15:00", "17:00")
            results.append("CREATED")
        except BookingError as error:
            results.append(error.code)

    threads = [threading.Thread(target=attempt, args=(uid,)) for uid in user_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(results) == ["CREATED", "SLOT_UNAVAILABLE"]


def test_api_requires_logged_in_user(app):
    client = app.test_client()
    response = book(client)
    assert response.status_code == 401
    assert response.get_json()["code"] == "UNAUTHENTICATED"

    login(client, ("admin@smashgo.local", "AdminTest123!"))
    assert book(client).status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"courtId": 1, "bookingDate": "not-a-date", "startTime": "08:00", "endTime": "10:00"},
        {"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:15", "endTime": "10:00"},
        {"courtId": "abc", "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    ],
)
def test_invalid_input_is_rejected(app, payload):
    client = app.test_client()
    login(client)

    response = client.post("/api/bookings", json=payload)

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_INPUT"


def test_unknown_court_is_not_found(app):
    client = app.test_client()
    login(client)
    assert book(client, courtId=999).status_code == 404


def test_guest_sees_book_page_with_selection_prefilled(app):
    client = app.test_client()

    response = client.get(f"/book?courtId=3&date={TOMORROW}&startTime=18:00&endTime=20:00")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'data-authenticated="false"' in page
    assert f'value="{TOMORROW}"' in page
    assert 'data-initial="18:00"' in page
    assert 'data-initial="20:00"' in page
    assert 'data-availability-url="/api/courts/0/availability"' in page
    assert 'id="booking-schedule-grid"' in page
    assert 'data-name="SmashGo Cầu Giấy 1"' in page
    assert "Chọn ô còn trống" in page
    selected_options = re.findall(r'<option value="(\d+)"[^>]*\bselected\b', page)
    assert selected_options == ["3"]


def test_login_returns_user_to_book_with_selection(app):
    client = app.test_client()
    next_url = f"/book?courtId=3&date={TOMORROW}&startTime=18:00&endTime=20:00&restored=1"

    response = client.post(
        "/login",
        data={"email": "user@smashgo.local", "password": "UserTest123!", "next": next_url},
    )
    assert response.status_code == 302
    assert response.location == next_url

    page = client.get(next_url).get_data(as_text=True)
    assert 'data-authenticated="true"' in page
    assert "Lựa chọn của bạn đã được giữ nguyên" in page


def test_manager_cannot_open_book_page(app):
    client = app.test_client()
    login(client, ("walking-skeleton-manager@smashgo.local", "ManagerTest123!"))
    assert client.get("/book").status_code == 403
