import sqlite3
from datetime import date, datetime, timedelta

import pytest

from app import create_app
from booking_service import BookingError, cancel_booking, list_my_bookings
from init_db import initialize_database

IN_TWO_DAYS = (date.today() + timedelta(days=2)).isoformat()
DEMO_USER = ("user@smashgo.local", "UserTest123!")
OTHER_USER = ("user2@smashgo.local", "User2Test123!")


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "smashgo.sqlite3"
    initialize_database(path)
    return path


@pytest.fixture
def client(database_path):
    return create_app({"TESTING": True, "DATABASE_PATH": str(database_path)}).test_client()


def login(client, account=DEMO_USER):
    email, secret = account
    assert client.post("/login", data={"email": email, "password": secret}).status_code == 302


def query(database_path, sql, params=()):
    with sqlite3.connect(database_path) as connection:
        return connection.execute(sql, params).fetchall()


def user_id(database_path, email):
    return query(database_path, "SELECT UserID FROM Users WHERE Email = ?", (email,))[0][0]


def seeded_booking_id(database_path, status):
    return query(
        database_path,
        "SELECT BookingID FROM Booking JOIN Users USING (UserID) WHERE Email = ? AND Status = ?",
        (DEMO_USER[0], status),
    )[0][0]


def test_list_shows_only_own_bookings_in_every_seeded_state(client):
    login(client)

    response = client.get("/api/bookings/mine")

    assert response.status_code == 200
    bookings = response.get_json()
    assert sorted(booking["status"] for booking in bookings) == [
        "CANCELLED",
        "COMPLETED",
        "CONFIRMED",
        "EXPIRED",
    ]
    by_status = {booking["status"]: booking for booking in bookings}
    assert by_status["CONFIRMED"]["canCancel"] is True
    assert by_status["CONFIRMED"]["refundIfCancelledNow"] == by_status["CONFIRMED"]["paidAmount"]
    assert by_status["COMPLETED"]["canCancel"] is False
    assert by_status["CANCELLED"]["refundAmount"] == by_status["CANCELLED"]["paidAmount"]
    assert by_status["EXPIRED"]["paymentStatus"] is None
    assert {"bookingId", "courtName", "bookingDate", "startTime", "endTime", "depositAmount", "holdExpiresAt"} <= set(
        bookings[0]
    )


def test_status_filter(client):
    login(client)
    confirmed = client.get("/api/bookings/mine?status=CONFIRMED").get_json()
    assert [booking["status"] for booking in confirmed] == ["CONFIRMED"]

    invalid = client.get("/api/bookings/mine?status=WHATEVER")
    assert invalid.status_code == 400
    assert invalid.get_json()["code"] == "INVALID_INPUT"


def test_pending_booking_is_listed_with_hold_and_expires_later(client, database_path):
    login(client)
    booking_id = client.post(
        "/api/bookings",
        json={"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    ).get_json()["bookingId"]

    pending = next(b for b in client.get("/api/bookings/mine").get_json() if b["bookingId"] == booking_id)
    assert pending["status"] == "PENDING"
    assert pending["holdExpiresAt"]

    later = datetime.now() + timedelta(minutes=11)
    listed = list_my_bookings(database_path, user_id(database_path, DEMO_USER[0]), now=later)
    assert next(b for b in listed if b["bookingId"] == booking_id)["status"] == "EXPIRED"


def test_list_requires_login(client):
    response = client.get("/api/bookings/mine")
    assert response.status_code == 401


def test_cancel_more_than_four_hours_before_refunds_in_full(client, database_path):
    login(client)
    booking_id = client.post(
        "/api/bookings",
        json={"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    ).get_json()["bookingId"]
    accounts = client.get("/api/bank-accounts").get_json()
    paid = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": accounts[0]["bankAccountId"], "paymentMethod": "BANK_TRANSFER"},
    )
    assert paid.status_code == 200
    assert query(database_path, "SELECT COUNT(*) FROM Notification WHERE BookingID = ?", (booking_id,)) == [(1,)]

    response = client.delete(f"/api/bookings/{booking_id}", json={"cancelReason": "Bận việc"})

    assert response.status_code == 200
    assert response.get_json() == {
        "bookingId": booking_id,
        "status": "CANCELLED",
        "refundAmount": 180000,
        "paymentStatus": "REFUNDED",
    }
    assert query(
        database_path, "SELECT Status, CancelReason FROM Booking WHERE BookingID = ?", (booking_id,)
    ) == [("CANCELLED", "Bận việc")]
    assert query(database_path, "SELECT COUNT(*) FROM Notification WHERE BookingID = ?", (booking_id,)) == [(0,)]


def test_cancel_within_four_hours_keeps_half_the_deposit(database_path):
    booking_id = seeded_booking_id(database_path, "CONFIRMED")
    date_text, start_text, paid = query(
        database_path,
        "SELECT BookingDate, StartTime, Amount FROM Booking JOIN Payment USING (BookingID) WHERE BookingID = ?",
        (booking_id,),
    )[0]
    starts_at = datetime.strptime(f"{date_text} {start_text}", "%Y-%m-%d %H:%M")

    result = cancel_booking(
        database_path,
        user_id(database_path, DEMO_USER[0]),
        booking_id,
        now=starts_at - timedelta(hours=3),
    )

    assert result["refundAmount"] == paid / 2
    assert result["paymentStatus"] == "PARTIALLY_REFUNDED"


def test_exactly_four_hours_before_is_late_cancellation(database_path):
    booking_id = seeded_booking_id(database_path, "CONFIRMED")
    date_text, start_text = query(
        database_path, "SELECT BookingDate, StartTime FROM Booking WHERE BookingID = ?", (booking_id,)
    )[0]
    starts_at = datetime.strptime(f"{date_text} {start_text}", "%Y-%m-%d %H:%M")

    result = cancel_booking(
        database_path, user_id(database_path, DEMO_USER[0]), booking_id, now=starts_at - timedelta(hours=4)
    )

    assert result["paymentStatus"] == "PARTIALLY_REFUNDED"


def test_cancel_unpaid_booking_has_no_refund(client):
    login(client)
    booking_id = client.post(
        "/api/bookings",
        json={"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    ).get_json()["bookingId"]

    response = client.delete(f"/api/bookings/{booking_id}")

    assert response.status_code == 200
    assert response.get_json()["refundAmount"] == 0
    assert response.get_json()["paymentStatus"] is None
    # The released slot can be booked again.
    again = client.post(
        "/api/bookings",
        json={"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    )
    assert again.status_code == 201


@pytest.mark.parametrize("status", ["CANCELLED", "COMPLETED", "EXPIRED"])
def test_finished_bookings_are_not_cancellable(client, database_path, status):
    login(client)

    response = client.delete(f"/api/bookings/{seeded_booking_id(database_path, status)}")

    assert response.status_code == 409
    assert response.get_json()["code"] == "BOOKING_NOT_CANCELLABLE"


def test_cannot_cancel_after_start(database_path):
    booking_id = seeded_booking_id(database_path, "CONFIRMED")
    with pytest.raises(BookingError) as rejected:
        cancel_booking(
            database_path,
            user_id(database_path, DEMO_USER[0]),
            booking_id,
            now=datetime.now() + timedelta(days=10),
        )
    assert rejected.value.code == "BOOKING_NOT_CANCELLABLE"


def test_only_owner_can_cancel(client, database_path):
    login(client, OTHER_USER)

    response = client.delete(f"/api/bookings/{seeded_booking_id(database_path, 'CONFIRMED')}")

    assert response.status_code == 403
    assert response.get_json()["code"] == "NOT_BOOKING_OWNER"
    assert client.delete("/api/bookings/9999").status_code == 404


def test_my_bookings_page_has_all_four_states(client):
    guest = client.get("/my-bookings")
    assert guest.status_code == 302

    login(client)
    page = client.get("/my-bookings").get_data(as_text=True)

    for state in ("loading", "empty", "error", "data"):
        assert f'data-state="{state}"' in page
    assert "hơn 4 giờ" in page
    assert 'id="cancel-dialog"' in page

