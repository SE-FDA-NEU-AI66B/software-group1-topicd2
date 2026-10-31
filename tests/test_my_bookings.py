from datetime import datetime, timedelta

import pytest
from support import (
    COURT_A,
    COURT_B,
    FIXED_NOW,
    IN_TWO_DAYS,
    MOCK_OTP,
    OTHER_USER,
    USER_ID,
    VERIFIED_ACCOUNT_ID,
    add_booking,
    add_payment,
    login,
    query,
)

IN_THREE_DAYS = (FIXED_NOW.date() + timedelta(days=3)).isoformat()
CONFIRMED_STARTS_AT = datetime.fromisoformat(f"{IN_THREE_DAYS} 18:00")


@pytest.fixture
def history(database_path):
    """The user's bookings in four states, keyed by status."""
    def days_ago(days):
        return (FIXED_NOW.date() - timedelta(days=days)).isoformat()

    confirmed = add_booking(
        database_path, COURT_B, IN_THREE_DAYS, "18:00", "20:00", "CONFIRMED", USER_ID, 160000
    )
    add_payment(database_path, confirmed, 160000)
    completed = add_booking(database_path, COURT_A, days_ago(7), "19:00", "21:00", "COMPLETED", USER_ID)
    add_payment(database_path, completed, 200000)
    cancelled = add_booking(database_path, COURT_A, days_ago(2), "07:00", "08:00", "CANCELLED", USER_ID, 100000)
    add_payment(database_path, cancelled, 100000, "REFUNDED", 100000)
    expired = add_booking(
        database_path,
        COURT_B,
        days_ago(1),
        "17:00",
        "18:00",
        "EXPIRED",
        USER_ID,
        80000,
        hold_expires_at=f"{days_ago(2)} 12:10:00",
    )
    return {"CONFIRMED": confirmed, "COMPLETED": completed, "CANCELLED": cancelled, "EXPIRED": expired}


def hold_booking(client):
    response = client.post(
        "/api/bookings",
        json={"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": "08:00", "endTime": "10:00"},
    )
    assert response.status_code == 201
    return response.get_json()["bookingId"]


def test_list_shows_only_own_bookings_in_every_state(client, database_path, history):
    add_booking(database_path, COURT_A, IN_TWO_DAYS, "12:00", "14:00")  # another user's booking
    login(client)

    response = client.get("/api/bookings/mine")

    assert response.status_code == 200
    bookings = response.get_json()
    assert sorted(booking["status"] for booking in bookings) == ["CANCELLED", "COMPLETED", "CONFIRMED", "EXPIRED"]
    by_status = {booking["status"]: booking for booking in bookings}
    assert by_status["CONFIRMED"]["canCancel"] is True
    assert by_status["CONFIRMED"]["refundIfCancelledNow"] == 160000
    assert by_status["COMPLETED"]["canCancel"] is False
    assert by_status["CANCELLED"]["refundAmount"] == by_status["CANCELLED"]["paidAmount"]
    assert by_status["EXPIRED"]["paymentStatus"] is None
    assert {"bookingId", "courtName", "bookingDate", "startTime", "endTime", "depositAmount", "holdExpiresAt"} <= set(
        bookings[0]
    )


def test_status_filter(client, history):
    login(client)
    confirmed = client.get("/api/bookings/mine?status=CONFIRMED").get_json()
    assert [booking["status"] for booking in confirmed] == ["CONFIRMED"]

    invalid = client.get("/api/bookings/mine?status=WHATEVER")
    assert invalid.status_code == 400
    assert invalid.get_json()["code"] == "INVALID_INPUT"


def test_pending_booking_is_listed_with_hold_and_expires_later(client, frozen_clock):
    login(client)
    booking_id = hold_booking(client)

    pending = next(b for b in client.get("/api/bookings/mine").get_json() if b["bookingId"] == booking_id)
    assert pending["status"] == "PENDING"
    assert pending["holdExpiresAt"] == "2030-01-07 09:10:00"

    frozen_clock.advance(minutes=10)
    listed = client.get("/api/bookings/mine").get_json()
    assert next(b for b in listed if b["bookingId"] == booking_id)["status"] == "EXPIRED"


def test_list_requires_login(client):
    response = client.get("/api/bookings/mine")
    assert response.status_code == 401


def test_cancel_more_than_four_hours_before_refunds_in_full(client, database_path):
    login(client)
    booking_id = hold_booking(client)
    client.post(f"/api/bookings/{booking_id}/payment/otp", json={"bankAccountId": VERIFIED_ACCOUNT_ID})
    paid = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "paymentMethod": "BANK_TRANSFER", "otp": MOCK_OTP},
    )
    assert paid.status_code == 200
    assert query(database_path, "SELECT COUNT(*) FROM Notification WHERE BookingID = ?", (booking_id,)) == [(1,)]

    response = client.delete(f"/api/bookings/{booking_id}", json={"cancelReason": "Bận việc"})

    assert response.status_code == 200
    assert response.get_json() == {
        "bookingId": booking_id,
        "status": "CANCELLED",
        "refundAmount": 200000,
        "paymentStatus": "REFUNDED",
    }
    assert query(
        database_path, "SELECT Status, CancelReason FROM Booking WHERE BookingID = ?", (booking_id,)
    ) == [("CANCELLED", "Bận việc")]
    assert query(database_path, "SELECT COUNT(*) FROM Notification WHERE BookingID = ?", (booking_id,)) == [(0,)]


@pytest.mark.parametrize(
    ("before_start", "refund", "payment_status"),
    [
        (timedelta(hours=4, minutes=1), 160000, "REFUNDED"),
        (timedelta(hours=4), 80000, "PARTIALLY_REFUNDED"),
        (timedelta(hours=3), 80000, "PARTIALLY_REFUNDED"),
    ],
)
def test_refund_depends_on_four_hour_notice(client, frozen_clock, history, before_start, refund, payment_status):
    login(client)
    frozen_clock.set(CONFIRMED_STARTS_AT - before_start)

    response = client.delete(f"/api/bookings/{history['CONFIRMED']}")

    assert response.status_code == 200
    assert response.get_json()["refundAmount"] == refund
    assert response.get_json()["paymentStatus"] == payment_status


def test_cancel_unpaid_booking_has_no_refund(client):
    login(client)
    booking_id = hold_booking(client)

    response = client.delete(f"/api/bookings/{booking_id}")

    assert response.status_code == 200
    assert response.get_json()["refundAmount"] == 0
    assert response.get_json()["paymentStatus"] is None
    # The released slot can be booked again.
    hold_booking(client)


@pytest.mark.parametrize("status", ["CANCELLED", "COMPLETED", "EXPIRED"])
def test_finished_bookings_are_not_cancellable(client, history, status):
    login(client)

    response = client.delete(f"/api/bookings/{history[status]}")

    assert response.status_code == 409
    assert response.get_json()["code"] == "BOOKING_NOT_CANCELLABLE"


def test_cannot_cancel_after_start(client, frozen_clock, history):
    login(client)
    frozen_clock.set(CONFIRMED_STARTS_AT)

    response = client.delete(f"/api/bookings/{history['CONFIRMED']}")

    assert response.status_code == 409
    assert response.get_json()["code"] == "BOOKING_NOT_CANCELLABLE"


def test_only_owner_can_cancel(client, history):
    login(client, OTHER_USER)

    response = client.delete(f"/api/bookings/{history['CONFIRMED']}")

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
