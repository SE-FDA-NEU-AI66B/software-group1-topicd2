import re
from contextlib import closing
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import clock
from database import get_db_connection

HOLD_MINUTES = 10
MIN_DURATION_MINUTES = 60
SLOT_STEP_MINUTES = 30
MAX_ACTIVE_BOOKINGS = 2
OCCUPYING_STATUSES = ("PENDING", "CONFIRMED", "CHECKED_IN")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$|^24:00$")
# BR2 reasons, all reported to API clients as BOOKING_RULE_VIOLATION.
RULE_VIOLATION_REASONS = {
    "BOOKING_TOO_SHORT",
    "BOOKING_GAP",
    "OUTSIDE_OPENING_HOURS",
    "BOOKING_IN_PAST",
}
# Payment OTP errors share the API codes of account verification but have
# their own messages.
REASON_CODES = {
    "PAYMENT_OTP_INVALID": "INVALID_OTP",
    "PAYMENT_OTP_EXPIRED_OR_LOCKED": "VERIFICATION_EXPIRED_OR_LOCKED",
}


@dataclass
class BookingError(Exception):
    reason: str
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def code(self) -> str:
        if self.reason in RULE_VIOLATION_REASONS:
            return "BOOKING_RULE_VIOLATION"
        return REASON_CODES.get(self.reason, self.reason)


def parse_minutes(value: str) -> int | None:
    if not isinstance(value, str) or not TIME_PATTERN.fullmatch(value):
        return None
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def format_minutes(total_minutes: int) -> str:
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def _parse_request(court_id: Any, booking_date: Any, start_time: Any, end_time: Any):
    try:
        clean_court_id = int(court_id)
        clean_date = date.fromisoformat(booking_date)
    except (TypeError, ValueError):
        raise BookingError("INVALID_INPUT") from None

    start_minutes = parse_minutes(start_time)
    end_minutes = parse_minutes(end_time)
    if (
        clean_court_id <= 0
        or start_minutes is None
        or end_minutes is None
        or start_minutes % SLOT_STEP_MINUTES
    ):
        raise BookingError("INVALID_INPUT")
    return clean_court_id, clean_date, start_minutes, end_minutes


def _release_expired_holds(connection, now: datetime) -> None:
    connection.execute(
        """
        UPDATE Booking SET Status = 'EXPIRED'
        WHERE Status = 'PENDING' AND HoldExpiresAt <= ?
        """,
        (now.strftime(DATETIME_FORMAT),),
    )


def _check_booking_rules(court, booking_date, start_minutes, end_minutes, now):
    if end_minutes - start_minutes < MIN_DURATION_MINUTES:
        raise BookingError("BOOKING_TOO_SHORT")

    open_minutes = parse_minutes(court["OpenTime"])
    close_minutes = parse_minutes(court["CloseTime"])
    if start_minutes < open_minutes or end_minutes > close_minutes:
        raise BookingError(
            "OUTSIDE_OPENING_HOURS",
            {"open_time": court["OpenTime"], "close_time": court["CloseTime"]},
        )

    starts_at = datetime.combine(booking_date, datetime.min.time()) + timedelta(
        minutes=start_minutes
    )
    if starts_at <= now:
        raise BookingError("BOOKING_IN_PAST")


def _check_slot(connection, court, booking_date, start_minutes, end_minutes):
    occupied = connection.execute(
        f"""
        SELECT StartTime, EndTime FROM Booking
        WHERE CourtID = ? AND BookingDate = ?
          AND Status IN ({", ".join("?" for _ in OCCUPYING_STATUSES)})
        UNION ALL
        SELECT StartTime, EndTime FROM Court_Block
        WHERE CourtID = ? AND BlockDate = ?
        ORDER BY StartTime
        """,
        (
            court["CourtID"],
            booking_date.isoformat(),
            *OCCUPYING_STATUSES,
            court["CourtID"],
            booking_date.isoformat(),
        ),
    ).fetchall()

    intervals = [(parse_minutes(row["StartTime"]), parse_minutes(row["EndTime"])) for row in occupied]
    for taken_start, taken_end in intervals:
        if start_minutes < taken_end and taken_start < end_minutes:
            raise BookingError(
                "SLOT_UNAVAILABLE",
                {
                    "court_name": court["CourtName"],
                    "start_time": format_minutes(taken_start),
                    "end_time": format_minutes(taken_end),
                },
            )

    # BR2: back-to-back bookings must touch; a gap shorter than the minimum
    # booking length could never be booked by anyone else.
    for taken_start, taken_end in intervals:
        gap = start_minutes - taken_end if taken_end <= start_minutes else taken_start - end_minutes
        if 0 < gap < MIN_DURATION_MINUTES:
            raise BookingError(
                "BOOKING_GAP",
                {
                    "gap_minutes": gap,
                    "start_time": format_minutes(taken_start),
                    "end_time": format_minutes(taken_end),
                },
            )


def _check_active_limit(connection, user_id: int, now: datetime) -> None:
    active_count = connection.execute(
        f"""
        SELECT COUNT(*) FROM Booking
        WHERE UserID = ?
          AND Status IN ({", ".join("?" for _ in OCCUPYING_STATUSES)})
          AND BookingDate || ' ' || EndTime > ?
        """,
        (user_id, *OCCUPYING_STATUSES, now.strftime("%Y-%m-%d %H:%M")),
    ).fetchone()[0]
    if active_count >= MAX_ACTIVE_BOOKINGS:
        raise BookingError("ACTIVE_BOOKING_LIMIT", {"limit": MAX_ACTIVE_BOOKINGS})


def create_booking(
    database_path: str | Path,
    user_id: int,
    court_id: Any,
    booking_date: Any,
    start_time: Any,
    end_time: Any,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create a PENDING booking with a payment hold (BR1, BR2, BR3, BR6).

    Raises BookingError with an API error code when a rule is broken.
    """
    clean_court_id, clean_date, start_minutes, end_minutes = _parse_request(
        court_id, booking_date, start_time, end_time
    )
    now = now or clock.now()

    with closing(get_db_connection(database_path)) as connection:
        connection.isolation_level = None
        # ADR-02: take the write lock before re-checking overlap, so concurrent
        # booking requests for the same slot are serialized.
        connection.execute("BEGIN IMMEDIATE")
        try:
            court = connection.execute(
                """
                SELECT CourtID, CourtName, PricePerHour, OpenTime, CloseTime
                FROM Court WHERE CourtID = ? AND Status = 'ACTIVE'
                """,
                (clean_court_id,),
            ).fetchone()
            if court is None:
                raise BookingError("COURT_NOT_FOUND")

            _check_booking_rules(court, clean_date, start_minutes, end_minutes, now)
            _release_expired_holds(connection, now)
            _check_slot(connection, court, clean_date, start_minutes, end_minutes)
            _check_active_limit(connection, user_id, now)

            total_amount = round(court["PricePerHour"] * (end_minutes - start_minutes) / 60)
            hold_expires_at = (now + timedelta(minutes=HOLD_MINUTES)).strftime(DATETIME_FORMAT)
            cursor = connection.execute(
                """
                INSERT INTO Booking (
                    UserID, CourtID, BookingDate, StartTime, EndTime,
                    TotalAmount, DepositAmount, Status, HoldExpiresAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
                """,
                (
                    user_id,
                    clean_court_id,
                    clean_date.isoformat(),
                    format_minutes(start_minutes),
                    format_minutes(end_minutes),
                    total_amount,
                    total_amount,
                    hold_expires_at,
                ),
            )
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise

    return {
        "bookingId": cursor.lastrowid,
        "status": "PENDING",
        "holdExpiresAt": hold_expires_at,
        "totalAmount": total_amount,
        "depositAmount": total_amount,
    }


BOOKING_STATUSES = ("PENDING", "CONFIRMED", "CHECKED_IN", "COMPLETED", "CANCELLED", "EXPIRED")
CANCELLABLE_STATUSES = ("PENDING", "CONFIRMED")
FULL_REFUND_NOTICE = timedelta(hours=4)
LATE_CANCEL_REFUND_RATE = 0.5


def _starts_at(row) -> datetime:
    return datetime.strptime(f"{row['BookingDate']} {row['StartTime']}", "%Y-%m-%d %H:%M")


def refund_for(paid_amount: float, starts_at: datetime, now: datetime) -> float:
    """BR4: full refund more than 4 hours before play, otherwise 50% is kept."""
    if starts_at - now > FULL_REFUND_NOTICE:
        return paid_amount
    return round(paid_amount * LATE_CANCEL_REFUND_RATE)


def list_my_bookings(
    database_path: str | Path,
    user_id: int,
    status: str | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    if status is not None and status not in BOOKING_STATUSES:
        raise BookingError("INVALID_STATUS_FILTER")
    now = now or clock.now()

    with closing(get_db_connection(database_path)) as connection, connection:
        _release_expired_holds(connection, now)
        rows = connection.execute(
            """
            SELECT Booking.BookingID, Court.CourtName, Court.Location,
                   Booking.BookingDate, Booking.StartTime, Booking.EndTime,
                   Booking.Status, Booking.DepositAmount, Booking.HoldExpiresAt,
                   Payment.Status AS PaymentStatus, Payment.Amount AS PaidAmount,
                   Payment.RefundAmount
            FROM Booking
            JOIN Court ON Court.CourtID = Booking.CourtID
            LEFT JOIN Payment ON Payment.BookingID = Booking.BookingID
            WHERE Booking.UserID = ? AND (? IS NULL OR Booking.Status = ?)
            ORDER BY Booking.BookingDate DESC, Booking.StartTime DESC
            """,
            (user_id, status, status),
        ).fetchall()

    bookings = []
    for row in rows:
        paid_amount = row["PaidAmount"] if row["PaymentStatus"] else 0
        cancellable = row["Status"] in CANCELLABLE_STATUSES and _starts_at(row) > now
        bookings.append(
            {
                "bookingId": row["BookingID"],
                "courtName": row["CourtName"],
                "location": row["Location"],
                "bookingDate": row["BookingDate"],
                "startTime": row["StartTime"],
                "endTime": row["EndTime"],
                "status": row["Status"],
                "depositAmount": row["DepositAmount"],
                "holdExpiresAt": row["HoldExpiresAt"] if row["Status"] == "PENDING" else None,
                "paymentStatus": row["PaymentStatus"],
                "paidAmount": paid_amount,
                "refundAmount": row["RefundAmount"],
                "canCancel": cancellable,
                "refundIfCancelledNow": (
                    refund_for(paid_amount, _starts_at(row), now) if cancellable else None
                ),
            }
        )
    return bookings


def cancel_booking(
    database_path: str | Path,
    user_id: int,
    booking_id: int,
    cancel_reason: Any = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Cancel the user's own booking and apply the BR4 refund policy."""
    now = now or clock.now()
    reason = cancel_reason.strip()[:255] if isinstance(cancel_reason, str) else ""

    with closing(get_db_connection(database_path)) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            _release_expired_holds(connection, now)
            booking = connection.execute(
                """
                SELECT UserID, BookingDate, StartTime, Status FROM Booking
                WHERE BookingID = ?
                """,
                (booking_id,),
            ).fetchone()
            if booking is None:
                raise BookingError("BOOKING_NOT_FOUND")
            if booking["UserID"] != user_id:
                raise BookingError("NOT_BOOKING_OWNER")
            if booking["Status"] not in CANCELLABLE_STATUSES or _starts_at(booking) <= now:
                raise BookingError("BOOKING_NOT_CANCELLABLE")

            payment = connection.execute(
                "SELECT PaymentID, Amount FROM Payment WHERE BookingID = ? AND Status = 'SUCCESS'",
                (booking_id,),
            ).fetchone()
            timestamp = now.strftime(DATETIME_FORMAT)
            refund_amount = 0
            payment_status = None
            if payment is not None:
                refund_amount = refund_for(payment["Amount"], _starts_at(booking), now)
                payment_status = (
                    "REFUNDED" if refund_amount == payment["Amount"] else "PARTIALLY_REFUNDED"
                )
                connection.execute(
                    """
                    UPDATE Payment SET Status = ?, RefundAmount = ?, RefundedAt = ?
                    WHERE PaymentID = ?
                    """,
                    (payment_status, refund_amount, timestamp, payment["PaymentID"]),
                )

            connection.execute(
                """
                UPDATE Booking
                SET Status = 'CANCELLED', CancelledAt = ?, CancelledBy = ?, CancelReason = ?
                WHERE BookingID = ?
                """,
                (timestamp, user_id, reason or None, booking_id),
            )
            # BR5: the reminder for a cancelled booking must not be sent.
            connection.execute(
                """
                DELETE FROM Notification
                WHERE BookingID = ? AND Type = 'BOOKING_REMINDER' AND SentAt IS NULL
                """,
                (booking_id,),
            )
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise

    return {
        "bookingId": booking_id,
        "status": "CANCELLED",
        "refundAmount": refund_amount,
        "paymentStatus": payment_status,
    }
