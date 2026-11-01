from support import (
    COURT_A,
    IN_TWO_DAYS,
    MOCK_OTP,
    OTHER_USER,
    VERIFIED_ACCOUNT_ID,
    login,
    query,
)


def hold_booking(client, start_time="08:00", end_time="10:00"):
    response = client.post(
        "/api/bookings",
        json={"courtId": COURT_A, "bookingDate": IN_TWO_DAYS, "startTime": start_time, "endTime": end_time},
    )
    assert response.status_code == 201
    return response.get_json()["bookingId"]


def link_account(client, bank_name="ACB", account_number="11112222"):
    response = client.post(
        "/api/bank-accounts",
        json={"bankName": bank_name, "accountNumber": account_number, "accountHolderName": "Nguyen Van A"},
    )
    assert response.status_code == 201
    return response.get_json()["bankAccountId"]


def link_and_verify(client, account_number="9704123456789"):
    account_id = link_account(client, "Vietcombank", account_number)
    verified = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})
    assert verified.status_code == 200
    return account_id


def pay(client, booking_id, account_id, otp=MOCK_OTP):
    sent = client.post(f"/api/bookings/{booking_id}/payment/otp", json={"bankAccountId": account_id})
    assert sent.status_code == 200
    return client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": account_id, "paymentMethod": "BANK_TRANSFER", "otp": otp},
    )


def booking_status(database_path, booking_id):
    return query(database_path, "SELECT Status FROM Booking WHERE BookingID = ?", (booking_id,))[0][0]


# TC-47: Bank account responses reveal only the last four digits, never the OTP or its hash.
def test_link_returns_only_last_four_digits(client, database_path, fake_gateway):
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
    assert fake_gateway.sent_otps == [("BIDV", "123456789012")]
    listed = client.get("/api/bank-accounts")
    assert {
        "bankAccountId": body["bankAccountId"],
        "bankName": "BIDV",
        "accountNumberLast4": "9012",
        "isVerified": False,
        "isPrimary": False,
    } in listed.get_json()
    assert "123456789012" not in listed.get_data(as_text=True)
    assert "0123456789" not in listed.get_data(as_text=True)
    otp_hash = query(
        database_path,
        "SELECT OTPHash FROM BankAccountVerification WHERE BankAccountID = ?",
        (body["bankAccountId"],),
    )[0][0]
    assert otp_hash not in response.get_data(as_text=True)
    assert otp_hash not in listed.get_data(as_text=True)
    assert MOCK_OTP not in response.get_data(as_text=True)
    assert MOCK_OTP not in listed.get_data(as_text=True)


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
    account_id = link_account(client)

    first = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    assert first.status_code == 400
    assert first.get_json()["code"] == "INVALID_OTP"
    assert "còn 2 lần" in first.get_json()["message"]
    client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    locked = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": "000000"})
    assert locked.status_code == 409
    assert locked.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"

    still_locked = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})
    assert still_locked.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"

    # Linking the same account again sends a new OTP.
    assert link_account(client) == account_id
    verified = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})
    assert verified.status_code == 200


def test_expired_otp_is_rejected(client, frozen_clock):
    login(client)
    account_id = link_account(client)

    frozen_clock.advance(minutes=5)
    response = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})

    assert response.status_code == 409
    assert response.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"


# TC-54: Verifying a bank account that does not exist returns 404.
def test_tc54_verifying_missing_bank_account_returns_not_found(client):
    login(client)

    response = client.post("/api/bank-accounts/9999/verify", json={"otp": MOCK_OTP})

    assert response.status_code == 404
    assert response.get_json()["code"] == "BANK_ACCOUNT_NOT_FOUND"


def test_otp_is_accepted_just_before_expiry(client, frozen_clock):
    login(client)
    account_id = link_account(client)

    frozen_clock.advance(minutes=4, seconds=59)
    response = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})

    assert response.status_code == 200


# TC-48: Linking an already verified bank account again is rejected.
def test_verified_account_cannot_be_linked_twice(client):
    login(client)
    link_and_verify(client)
    again = client.post(
        "/api/bank-accounts",
        json={"bankName": "Vietcombank", "accountNumber": "9704123456789", "accountHolderName": "Nguyen Van A"},
    )
    assert again.status_code == 409
    assert again.get_json()["code"] == "BANK_ACCOUNT_EXISTS"


# TC-55: Verifying another user's bank account returns 403 NOT_ACCOUNT_OWNER.
def test_cannot_verify_another_users_account(client):
    login(client)
    account_id = link_account(client)
    client.get("/logout")
    login(client, OTHER_USER)

    response = client.post(f"/api/bank-accounts/{account_id}/verify", json={"otp": MOCK_OTP})

    assert response.status_code == 403
    assert response.get_json()["code"] == "NOT_ACCOUNT_OWNER"


# TC-37: A valid payment confirms the booking, records one payment, schedules a reminder, and cannot be repeated.
def test_payment_confirms_booking_and_schedules_reminder(client, database_path, fake_gateway):
    login(client)
    booking_id = hold_booking(client)

    response = pay(client, booking_id, VERIFIED_ACCOUNT_ID)

    assert response.status_code == 200
    assert response.get_json()["status"] == "CONFIRMED"
    assert response.get_json()["paymentStatus"] == "SUCCESS"
    assert booking_status(database_path, booking_id) == "CONFIRMED"
    assert query(database_path, "SELECT Amount, Status FROM Payment WHERE BookingID = ?", (booking_id,)) == [
        (200000, "SUCCESS")
    ]
    assert fake_gateway.charges == [("Vietcombank", "0123456789", 200000)]
    assert query(
        database_path, "SELECT Type, ScheduledAt FROM Notification WHERE BookingID = ?", (booking_id,)
    ) == [("BOOKING_REMINDER", f"{IN_TWO_DAYS} 04:00:00")]

    paid_again = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": VERIFIED_ACCOUNT_ID})
    assert paid_again.status_code == 409
    assert paid_again.get_json()["code"] == "HOLD_EXPIRED_OR_ALREADY_PAID"


# TC-41: An unverified account cannot pay, and the booking remains pending.
def test_unverified_account_cannot_pay(client, database_path):
    login(client)
    booking_id = hold_booking(client)
    account_id = link_account(client)

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 422
    assert response.get_json()["code"] == "BANK_ACCOUNT_NOT_VERIFIED"
    assert booking_status(database_path, booking_id) == "PENDING"


# TC-50: A failed charge leaves the booking pending without a payment row.
def test_gateway_failure_keeps_booking_pending(client, database_path, fake_gateway):
    login(client)
    booking_id = hold_booking(client)
    fake_gateway.fail_charges = True

    response = pay(client, booking_id, VERIFIED_ACCOUNT_ID)

    assert response.status_code == 502
    assert response.get_json()["code"] == "PAYMENT_FAILED"
    assert booking_status(database_path, booking_id) == "PENDING"
    assert query(database_path, "SELECT COUNT(*) FROM Payment WHERE BookingID = ?", (booking_id,)) == [(0,)]

    # The OTP was used up by the failed attempt; a retry needs a new one.
    retry = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": MOCK_OTP},
    )
    assert retry.status_code == 409
    assert retry.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"


# TC-44: Two wrong OTP attempts still permit payment with the correct OTP.
def test_payment_requires_otp_sent_to_the_account(client, database_path, fake_gateway):
    login(client)
    booking_id = hold_booking(client)
    primary = next(account for account in client.get("/api/bank-accounts").get_json() if account["isPrimary"])

    without_otp = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": primary["bankAccountId"]})
    assert without_otp.status_code == 409
    assert without_otp.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"
    assert "Gửi lại mã" in without_otp.get_json()["message"]

    sent = client.post(f"/api/bookings/{booking_id}/payment/otp", json={"bankAccountId": primary["bankAccountId"]})
    assert sent.status_code == 200
    assert sent.get_json()["accountNumberLast4"] == primary["accountNumberLast4"]
    assert fake_gateway.sent_otps == [("Vietcombank", "0123456789")]

    wrong = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": primary["bankAccountId"], "otp": "000000"},
    )
    assert wrong.status_code == 400
    assert wrong.get_json()["code"] == "INVALID_OTP"
    assert "thanh toán" in wrong.get_json()["message"]
    assert booking_status(database_path, booking_id) == "PENDING"

    wrong_again = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": primary["bankAccountId"], "otp": "000000"},
    )
    assert wrong_again.status_code == 400
    assert wrong_again.get_json()["code"] == "INVALID_OTP"

    right = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": primary["bankAccountId"], "otp": MOCK_OTP},
    )
    assert right.status_code == 200


# TC-45: Three wrong OTP attempts lock the payment verification.
def test_payment_otp_locks_after_three_wrong_attempts(client):
    login(client)
    booking_id = hold_booking(client)
    client.post(f"/api/bookings/{booking_id}/payment/otp", json={"bankAccountId": VERIFIED_ACCOUNT_ID})

    codes = [
        client.post(
            f"/api/bookings/{booking_id}/payment", json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": "000000"}
        ).get_json()["code"]
        for _ in range(3)
    ]
    assert codes == ["INVALID_OTP", "INVALID_OTP", "VERIFICATION_EXPIRED_OR_LOCKED"]

    still_locked = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": MOCK_OTP},
    )
    assert still_locked.status_code == 409
    assert still_locked.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"


def test_payment_otp_requires_verified_account(client):
    login(client)
    booking_id = hold_booking(client)
    account_id = link_account(client)

    response = client.post(f"/api/bookings/{booking_id}/payment/otp", json={"bankAccountId": account_id})

    assert response.status_code == 422
    assert response.get_json()["code"] == "BANK_ACCOUNT_NOT_VERIFIED"


# TC-49: The first verified bank account remains the only primary account.
def test_first_linked_account_stays_primary(client):
    login(client)
    seeded_primary = client.get("/api/bank-accounts").get_json()[0]
    assert seeded_primary["isPrimary"] is True

    new_account_id = link_and_verify(client)
    accounts = client.get("/api/bank-accounts").get_json()

    assert [account["bankAccountId"] for account in accounts if account["isPrimary"]] == [
        seeded_primary["bankAccountId"]
    ]
    assert accounts[-1]["bankAccountId"] == new_account_id


# TC-39: Just after the ten-minute hold expires, payment is rejected and the slot is released.
def test_expired_hold_cannot_be_paid(client, frozen_clock, database_path):
    login(client)
    booking_id = hold_booking(client)
    sent = client.post(
        f"/api/bookings/{booking_id}/payment/otp",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID},
    )
    assert sent.status_code == 200

    frozen_clock.advance(minutes=10, seconds=1)
    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": VERIFIED_ACCOUNT_ID})

    assert response.status_code == 409
    assert response.get_json()["code"] == "HOLD_EXPIRED_OR_ALREADY_PAID"
    assert client.get(f"/book?bookingId={booking_id}").get_data(as_text=True).count("không còn chờ thanh toán") == 1
    bookings = client.get("/api/bookings/mine").get_json()
    assert next(booking for booking in bookings if booking["bookingId"] == booking_id)["status"] == "EXPIRED"

    client.get("/logout")
    login(client, OTHER_USER)
    replacement = hold_booking(client)
    assert replacement != booking_id


# TC-38: A booking can still be paid one second before its ten-minute hold expires.
def test_hold_can_still_be_paid_one_second_before_expiry(client, frozen_clock, database_path):
    login(client)
    booking_id = hold_booking(client)

    frozen_clock.advance(minutes=9, seconds=59)

    response = pay(client, booking_id, VERIFIED_ACCOUNT_ID)

    assert response.status_code == 200
    assert booking_status(database_path, booking_id) == "CONFIRMED"


# TC-46: Payment requires authentication and booking ownership; a missing booking returns 404.
def test_only_owner_can_pay(client):
    login(client)
    booking_id = hold_booking(client)
    client.get("/logout")

    unauthenticated = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": MOCK_OTP},
    )
    assert unauthenticated.status_code == 401
    assert unauthenticated.get_json()["code"] == "UNAUTHENTICATED"

    login(client, OTHER_USER)
    account_id = link_and_verify(client)

    response = client.post(f"/api/bookings/{booking_id}/payment", json={"bankAccountId": account_id})

    assert response.status_code == 403
    assert response.get_json()["code"] == "NOT_BOOKING_OWNER"
    missing = client.post(
        "/api/bookings/9999/payment",
        json={"bankAccountId": account_id, "otp": MOCK_OTP},
    )
    assert missing.status_code == 404
    assert missing.get_json()["code"] == "BOOKING_NOT_FOUND"


# TC-42: A payment OTP is valid 4 minutes and 59 seconds after it is issued.
def test_payment_otp_is_valid_at_4_minutes_59_seconds(client, frozen_clock, database_path):
    login(client)
    booking_id = hold_booking(client)
    sent = client.post(
        f"/api/bookings/{booking_id}/payment/otp",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID},
    )
    assert sent.status_code == 200
    frozen_clock.advance(minutes=4, seconds=59)

    response = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": MOCK_OTP},
    )

    assert response.status_code == 200
    assert booking_status(database_path, booking_id) == "CONFIRMED"


# TC-43: A payment OTP has expired 5 minutes and 1 second after it is issued.
def test_payment_otp_expires_after_five_minutes(client, frozen_clock, database_path):
    login(client)
    booking_id = hold_booking(client)
    sent = client.post(
        f"/api/bookings/{booking_id}/payment/otp",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID},
    )
    assert sent.status_code == 200
    frozen_clock.advance(minutes=5, seconds=1)

    response = client.post(
        f"/api/bookings/{booking_id}/payment",
        json={"bankAccountId": VERIFIED_ACCOUNT_ID, "otp": MOCK_OTP},
    )

    assert response.status_code == 409
    assert response.get_json()["code"] == "VERIFICATION_EXPIRED_OR_LOCKED"
    assert booking_status(database_path, booking_id) == "PENDING"


def test_payment_step_page(client):
    assert client.get("/book?bookingId=1").status_code == 302

    login(client)
    booking_id = hold_booking(client)
    page = client.get(f"/book?bookingId={booking_id}").get_data(as_text=True)

    assert f'data-booking-id="{booking_id}"' in page
    assert 'data-seconds-left="600"' in page
    assert "200.000đ" in page
    assert "Vietcombank" in page
