import sqlite3
from datetime import date, datetime, timedelta

import pytest

import bank_gateway
from app import create_app
from booking_service import BookingError
from init_db import initialize_database
from payment_service import link_bank_account, verify_bank_account

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


def hold_booking(client, start_time="08:00", end_time="10:00"):
    response = client.post(
        "/api/bookings",
        json={"courtId": 1, "bookingDate": IN_TWO_DAYS, "startTime": start_time, "endTime": end_time},
    )
    assert response.status_code == 201
    return response.get_json()["bookingId"]


def link_and_verify(client, account_number="9704123456789"):
    linked = client.post(
        "/api/bank-accounts",
        json={"bankName": "Vietcombank", "accountNumber": account_number, "accountHolderName": "Nguyen Van A"},
    )
    assert linked.status_code == 201
    account_id = linked.get_json()["bankAccountId"]
    verified = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": bank_gateway.MOCK_OTP})
    assert verified.status_code == 200
    return account_id


def query(database_path, sql, params=()):
    with sqlite3.connect(database_path) as connection:
        return connection.execute(sql, params).fetchall()


def test_link_returns_only_last_four_digits(client):
    login(client)

    response = client.post(
        "/api/bank-accounts",
        json={"bankName": "BIDV", "accountNumber": "1234 5678 9012", "accountHolderName": "Nguyen Van A"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body == {
        "bankAccountId": body["bankAccountId"],
        "bankName": "BIDV",
        "accountNumberLast4": "9012",
        "verificationStatus": "PENDING",
    }
    listed = client.get("/api/bank-accounts")
    assert {
        "bankAccountId": body["bankAccountId"],
        "bankName": "BIDV",
        "accountNumberLast4": "9012",
        "isVerified": False,
    } in listed.get_json()
    assert "123456789012" not in listed.get_data(as_text=True)
    assert "0123456789" not in listed.get_data(as_text=True)


def test_invalid_account_input_is_rejected(client):
    login(client)
    response = client.post(
        "/api/bank-accounts",
        json={"bankName": "Unknown Bank", "accountNumber": "12", "accountHolderName": ""},
    )
    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_INPUT"


def test_wrong_otp_three_times_locks_verification(client):
    login(client)
    account_id = client.post(
        "/api/bank-accounts",
        json={"bankName": "ACB", "accountNumber": "11112222", "accountHolderName": "Nguyen Van A"},
    ).get_json()["bankAccountId"]

    first = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    assert first.status_code == 400
    assert first.get_json()["code"] == "INVALID_OTP"
    assert "còn 2 lần" in first.get_json()["message"]
    client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    locked = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    assert locked.status_code == 409
    assert locked.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"

    still_locked = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": bank_gateway.MOCK_OTP})
    assert still_locked.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"

    # Linking the same account again sends a new OTP.
    relinked = client.post(
        "/api/bank-accounts",
        json={"bankName": "ACB", "accountNumber": "11112222", "accountHolderName": "Nguyen Van A"},
    )
    assert relinked.status_code == 201
    assert relinked.get_json()["bankAccountId"] == account_id
    verified = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": bank_gateway.MOCK_OTP})
    assert verified.status_code == 200


def test_expired_otp_is_rejected(database_path):
    user_id = query(database_path, "SELECT UserID FROM Users WHERE Email = ?", (DEMO_USER[0],))[0][0]
    now = datetime.now()
    account = link_bank_account(database_path, user_id, "MB Bank", "55556666", "Nguyen Van A", now=now)

    with pytest.raises(BookingError) as rejected:
        verify_bank_account(
            database_path, user_id, account["bankAccountId"], bank_gateway.MOCK_OTP, now=now + timedelta(minutes=6)
        )
    assert rejected.value.code == "VERIFICATION_EXPIRED_OR_LOCKED"


def test_verified_account_cannot_be_linked_twice(client):
    login(client)
    link_and_verify(client)
    again = client.post(
        "/api/bank-accounts",
        json={"bankName": "Vietcombank", "accountNumber": "9704123456789", "accountHolderName": "Nguyen Van A"},
    )
    assert again.status_code == 409
    assert again.get_json()["code"] == "BANK_ACCOUNT_EXISTS"


def test_cannot_verify_another_users_account(client):
    login(client)
    account_id = client.post(
        "/api/bank-accounts",
        json={"bankName": "ACB", "accountNumber": "11112222", "accountHolderName": "Nguyen Van A"},
    ).get_json()["bankAccountId"]
    client.get("/logout")
    login(client, OTHER_USER)

    response = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": bank_gateway.MOCK_OTP})

    assert response.status_code == 403
    assert response.get_json()["code"] == "NOT_ACCOUNT_OWNER"


def test_payment_confirms_booking_and_schedules_reminder(client, database_path):
    login(client)
    booking_id = hold_booking(client)
    account_id = link_and_verify(client)

    response = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": account_id, "paymentMethod": "BANK_TRANSFER"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "CONFIRMED"
    assert response.get_json()["paymentStatus"] == "SUCCESS"
    assert query(database_path, "SELECT Status FROM Booking WHERE BookingID = ?", (booking_id,)) == [("CONFIRMED",)]
    assert query(database_path, "SELECT Amount, Status FROM Payment WHERE BookingID = ?", (booking_id,)) == [
        (180000, "SUCCESS")
    ]
    assert query(
        database_path, "SELECT Type, ScheduledAt FROM Notification WHERE BookingID = ?", (booking_id,)
    ) == [("BOOKING_REMINDER", f"{IN_TWO_DAYS} 04:00:00")]

    paid_again = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})
    assert paid_again.status_code == 409
    assert paid_again.get_json()["code"] == "HOLD_EXPIRED_OR_ALREADY_PAID"


def test_unverified_account_cannot_pay(client):
    login(client)
    booking_id = hold_booking(client)
    account_id = client.post(
        "/api/bank-accounts",
        json={"bankName": "ACB", "accountNumber": "11112222", "accountHolderName": "Nguyen Van A"},
    ).get_json()["bankAccountId"]

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 422
    assert response.get_json()["code"] == "BANK_ACCOUNT_NOT_VERIFIED"


def test_gateway_failure_keeps_booking_pending(client, database_path):
    login(client)
    booking_id = hold_booking(client)
    account_id = link_and_verify(client, account_number="123450000")

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 502
    assert response.get_json()["code"] == "PAYMENT_FAILED"
    assert query(database_path, "SELECT Status FROM Booking WHERE BookingID = ?", (booking_id,)) == [("PENDING",)]
    assert query(database_path, "SELECT COUNT(*) FROM Payment WHERE BookingID = ?", (booking_id,)) == [(0,)]


def test_expired_hold_cannot_be_paid(client, database_path):
    login(client)
    booking_id = hold_booking(client)
    account_id = link_and_verify(client)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE Booking SET HoldExpiresAt = ? WHERE BookingID = ?",
            ((datetime.now() - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"), booking_id),
        )

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 409
    assert response.get_json()["code"] == "HOLD_EXPIRED_OR_ALREADY_PAID"
    assert client.get(f"/book?bookingId={booking_id}").get_data(as_text=True).count("không còn chờ thanh toán") == 1


def test_only_owner_can_pay(client):
    login(client)
    booking_id = hold_booking(client)
    client.get("/logout")
    login(client, OTHER_USER)
    account_id = link_and_verify(client)

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 403
    assert response.get_json()["code"] == "NOT_BOOKING_OWNER"
    assert client.post("/api/bookings/9999/payment", json={"bankAccountId": account_id}).status_code == 404


def test_payment_step_page(client):
    assert client.get("/book?bookingId=1").status_code == 302

    login(client)
    booking_id = hold_booking(client)
    page = client.get(f"/book?bookingId={booking_id}").get_data(as_text=True)

    assert f'data-booking-id="{booking_id}"' in page
    seconds_left = int(page.split('data-seconds-left="')[1].split('"')[0])
    assert 590 <= seconds_left <= 600
    assert "180.000đ" in page
    assert "Vietcombank" in page
