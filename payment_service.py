import re
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

import bank_gateway
from booking_service import DATETIME_FORMAT, BookingError
from database import get_db_connection

OTP_VALID_MINUTES = 5
MAX_OTP_ATTEMPTS = 3
ACCOUNT_NUMBER_PATTERN = re.compile(r"^\d{6,19}$")
PAYMENT_METHOD = "BANK_TRANSFER"


def list_bank_accounts(database_path: str | Path, user_id: int) -> list[dict[str, Any]]:
    """List the user's accounts, oldest first.

    The first verified account (the one linked first) is the primary account:
    payment uses it by default and its OTP goes to it.
    """
    with closing(get_db_connection(database_path)) as connection:
        rows = connection.execute(
            """
            SELECT BankAccountID, BankName, AccountNumber, IsVerified
            FROM BankAccount WHERE UserID = ?
            ORDER BY BankAccountID
            """,
            (user_id,),
        ).fetchall()

    primary_id = next((row["BankAccountID"] for row in rows if row["IsVerified"]), None)
    return [
        {
            "bankAccountId": row["BankAccountID"],
            "bankName": row["BankName"],
            "accountNumberLast4": row["AccountNumber"][-4:],
            "isVerified": bool(row["IsVerified"]),
            "isPrimary": row["BankAccountID"] == primary_id,
        }
        for row in rows
    ]


def _start_otp(connection, bank_account_id: int, bank_name: str, account_number: str, now: datetime) -> str:
    """Send a new OTP to the account, replacing any OTP still pending."""
    connection.execute(
        """
        UPDATE BankAccountVerification SET Status = 'EXPIRED'
        WHERE BankAccountID = ? AND Status = 'PENDING'
        """,
        (bank_account_id,),
    )
    otp = bank_gateway.send_otp(bank_name, account_number)
    expires_at = (now + timedelta(minutes=OTP_VALID_MINUTES)).strftime(DATETIME_FORMAT)
    connection.execute(
        """
        INSERT INTO BankAccountVerification (BankAccountID, OTPHash, ExpiresAt, Status)
        VALUES (?, ?, ?, 'PENDING')
        """,
        (bank_account_id, generate_password_hash(otp), expires_at),
    )
    return expires_at


def _consume_otp(connection, bank_account_id: int, otp: Any, now: datetime, reasons: tuple[str, str]) -> str:
    """Check the latest pending OTP of the account and mark it VERIFIED.

    `reasons` names the (wrong OTP, expired or locked) errors to raise. Wrong
    attempts and expiry are written before raising, so callers must commit
    even when this raises.
    """
    invalid_reason, expired_reason = reasons
    verification = connection.execute(
        """
        SELECT VerificationID, OTPHash, ExpiresAt, AttemptCount FROM BankAccountVerification
        WHERE BankAccountID = ? AND Status = 'PENDING'
        ORDER BY VerificationID DESC LIMIT 1
        """,
        (bank_account_id,),
    ).fetchone()
    if verification is None:
        raise BookingError(expired_reason)
    if verification["ExpiresAt"] <= now.strftime(DATETIME_FORMAT):
        connection.execute(
            "UPDATE BankAccountVerification SET Status = 'EXPIRED' WHERE VerificationID = ?",
            (verification["VerificationID"],),
        )
        raise BookingError(expired_reason)

    if not isinstance(otp, str) or not check_password_hash(verification["OTPHash"], otp.strip()):
        attempts = verification["AttemptCount"] + 1
        locked = attempts >= MAX_OTP_ATTEMPTS
        connection.execute(
            """
            UPDATE BankAccountVerification SET AttemptCount = ?, Status = ?
            WHERE VerificationID = ?
            """,
            (attempts, "FAILED" if locked else "PENDING", verification["VerificationID"]),
        )
        if locked:
            raise BookingError(expired_reason)
        raise BookingError(invalid_reason, {"attempts_left": MAX_OTP_ATTEMPTS - attempts})

    verified_at = now.strftime(DATETIME_FORMAT)
    connection.execute(
        """
        UPDATE BankAccountVerification SET Status = 'VERIFIED', VerifiedAt = ?
        WHERE VerificationID = ?
        """,
        (verified_at, verification["VerificationID"]),
    )
    return verified_at


def link_bank_account(
    database_path: str | Path,
    user_id: int,
    bank_name: Any,
    account_number: Any,
    account_holder_name: Any,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Link an account and start OTP verification (BR7).

    Linking an account that exists but is not verified yet starts a new
    verification, so a user whose OTP expired can request another one.
    """
    clean_bank = bank_name.strip() if isinstance(bank_name, str) else ""
    clean_number = re.sub(r"\s+", "", account_number) if isinstance(account_number, str) else ""
    clean_holder = account_holder_name.strip() if isinstance(account_holder_name, str) else ""
    if (
        clean_bank not in bank_gateway.SUPPORTED_BANKS
        or not ACCOUNT_NUMBER_PATTERN.fullmatch(clean_number)
        or not clean_holder
    ):
        raise BookingError("INVALID_BANK_ACCOUNT_INPUT")

    now = now or datetime.now()
    with closing(get_db_connection(database_path)) as connection, connection:
        account = connection.execute(
            """
            SELECT BankAccountID, IsVerified FROM BankAccount
            WHERE UserID = ? AND BankName = ? AND AccountNumber = ?
            """,
            (user_id, clean_bank, clean_number),
        ).fetchone()
        if account and account["IsVerified"]:
            raise BookingError("BANK_ACCOUNT_EXISTS")

        if account is None:
            cursor = connection.execute(
                """
                INSERT INTO BankAccount (UserID, BankName, AccountNumber, AccountHolderName)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, clean_bank, clean_number, clean_holder),
            )
            account_id = cursor.lastrowid
        else:
            account_id = account["BankAccountID"]
            connection.execute(
                "UPDATE BankAccount SET AccountHolderName = ? WHERE BankAccountID = ?",
                (clean_holder, account_id),
            )

        _start_otp(connection, account_id, clean_bank, clean_number, now)

    return {
        "bankAccountId": account_id,
        "bankName": clean_bank,
        "accountNumberLast4": clean_number[-4:],
        "verificationStatus": "PENDING",
    }


def verify_bank_account(
    database_path: str | Path,
    user_id: int,
    bank_account_id: int,
    otp: Any,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now()
    with closing(get_db_connection(database_path)) as connection, connection:
        account = connection.execute(
            "SELECT UserID, IsVerified, VerifiedAt FROM BankAccount WHERE BankAccountID = ?",
            (bank_account_id,),
        ).fetchone()
        if account is None:
            raise BookingError("BANK_ACCOUNT_NOT_FOUND")
        if account["UserID"] != user_id:
            raise BookingError("NOT_ACCOUNT_OWNER")
        if account["IsVerified"]:
            return {
                "bankAccountId": bank_account_id,
                "isVerified": True,
                "verifiedAt": account["VerifiedAt"],
            }

        try:
            verified_at = _consume_otp(
                connection,
                bank_account_id,
                otp,
                now,
                ("INVALID_OTP", "VERIFICATION_EXPIRED_OR_LOCKED"),
            )
        except BookingError:
            # Keep the attempt count; leaving the block with an error rolls back.
            connection.commit()
            raise
        connection.execute(
            "UPDATE BankAccount SET IsVerified = 1, VerifiedAt = ? WHERE BankAccountID = ?",
            (verified_at, bank_account_id),
        )

    return {"bankAccountId": bank_account_id, "isVerified": True, "verifiedAt": verified_at}


def _payable_booking(connection, user_id: int, booking_id: int, now: datetime):
    booking = connection.execute(
        """
        SELECT Booking.UserID, Booking.BookingDate, Booking.StartTime,
               Booking.Status, Booking.HoldExpiresAt, Booking.DepositAmount,
               Booking.ReminderOffsetMinutes, Court.CourtName
        FROM Booking JOIN Court ON Court.CourtID = Booking.CourtID
        WHERE Booking.BookingID = ?
        """,
        (booking_id,),
    ).fetchone()
    if booking is None:
        raise BookingError("BOOKING_NOT_FOUND")
    if booking["UserID"] != user_id:
        raise BookingError("NOT_BOOKING_OWNER")
    if booking["Status"] != "PENDING" or booking["HoldExpiresAt"] <= now.strftime(DATETIME_FORMAT):
        raise BookingError("HOLD_EXPIRED_OR_ALREADY_PAID")
    return booking


def _verified_account(connection, user_id: int, bank_account_id: Any):
    account = None
    if isinstance(bank_account_id, int) and not isinstance(bank_account_id, bool):
        account = connection.execute(
            """
            SELECT BankName, AccountNumber, IsVerified FROM BankAccount
            WHERE BankAccountID = ? AND UserID = ?
            """,
            (bank_account_id, user_id),
        ).fetchone()
    if account is None or not account["IsVerified"]:
        raise BookingError("BANK_ACCOUNT_NOT_VERIFIED")
    return account


def request_payment_otp(
    database_path: str | Path,
    user_id: int,
    booking_id: int,
    bank_account_id: Any,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Send the OTP that authorises paying a held booking from a verified account."""
    now = now or datetime.now()
    with closing(get_db_connection(database_path)) as connection, connection:
        _payable_booking(connection, user_id, booking_id, now)
        account = _verified_account(connection, user_id, bank_account_id)
        expires_at = _start_otp(
            connection, bank_account_id, account["BankName"], account["AccountNumber"], now
        )

    return {
        "bankAccountId": bank_account_id,
        "bankName": account["BankName"],
        "accountNumberLast4": account["AccountNumber"][-4:],
        "otpExpiresAt": expires_at,
    }


def pay_booking(
    database_path: str | Path,
    user_id: int,
    booking_id: int,
    bank_account_id: Any,
    otp: Any,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Pay a held booking once the payment OTP is confirmed (BR3, BR5, BR7)."""
    now = now or datetime.now()
    with closing(get_db_connection(database_path)) as connection:
        connection.isolation_level = None
        # Serialize with other writers so a booking cannot be paid twice.
        connection.execute("BEGIN IMMEDIATE")
        try:
            booking = _payable_booking(connection, user_id, booking_id, now)
            account = _verified_account(connection, user_id, bank_account_id)
            _consume_otp(
                connection,
                bank_account_id,
                otp,
                now,
                ("PAYMENT_OTP_INVALID", "PAYMENT_OTP_EXPIRED_OR_LOCKED"),
            )

            transaction_code = bank_gateway.charge(
                account["BankName"], account["AccountNumber"], booking["DepositAmount"]
            )
            if transaction_code is None:
                raise BookingError("PAYMENT_FAILED")

            paid_at = now.strftime(DATETIME_FORMAT)
            connection.execute(
                "UPDATE Booking SET Status = 'CONFIRMED' WHERE BookingID = ?",
                (booking_id,),
            )
            connection.execute(
                """
                INSERT INTO Payment (
                    BookingID, BankAccountID, Amount, PaymentMethod, TransactionCode,
                    Status, PaidAt
                ) VALUES (?, ?, ?, ?, ?, 'SUCCESS', ?)
                """,
                (
                    booking_id,
                    bank_account_id,
                    booking["DepositAmount"],
                    PAYMENT_METHOD,
                    transaction_code,
                    paid_at,
                ),
            )
            starts_at = datetime.strptime(
                f"{booking['BookingDate']} {booking['StartTime']}", "%Y-%m-%d %H:%M"
            )
            reminder_at = starts_at - timedelta(minutes=booking["ReminderOffsetMinutes"])
            connection.execute(
                """
                INSERT INTO Notification (UserID, BookingID, Title, Message, Type, ScheduledAt)
                VALUES (?, ?, ?, ?, 'BOOKING_REMINDER', ?)
                """,
                (
                    user_id,
                    booking_id,
                    "Sắp đến giờ chơi",
                    (
                        f"Lịch chơi tại {booking['CourtName']} bắt đầu lúc "
                        f"{booking['StartTime']} ngày {booking['BookingDate']}."
                    ),
                    reminder_at.strftime(DATETIME_FORMAT),
                ),
            )
            connection.execute("COMMIT")
        except BookingError:
            # Keep OTP attempts and the used OTP; nothing else was written.
            connection.execute("COMMIT")
            raise
        except BaseException:
            connection.execute("ROLLBACK")
            raise

    return {
        "bookingId": booking_id,
        "status": "CONFIRMED",
        "paymentStatus": "SUCCESS",
        "paidAt": paid_at,
    }
