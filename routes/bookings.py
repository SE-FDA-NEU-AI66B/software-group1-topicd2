from contextlib import closing
from datetime import date, datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import bank_gateway
from booking_service import DATETIME_FORMAT, BookingError, create_booking
from database import get_db_connection
from errors import user_message
from payment_service import pay_booking
from routes.auth import default_url_for_role

bookings_bp = Blueprint("bookings", __name__)

ERROR_STATUSES = {
    "INVALID_INPUT": 400,
    "INVALID_OTP": 400,
    "UNAUTHENTICATED": 401,
    "FORBIDDEN": 403,
    "NOT_ACCOUNT_OWNER": 403,
    "NOT_BOOKING_OWNER": 403,
    "COURT_NOT_FOUND": 404,
    "BOOKING_NOT_FOUND": 404,
    "BANK_ACCOUNT_NOT_FOUND": 404,
    "SLOT_UNAVAILABLE": 409,
    "ACTIVE_BOOKING_LIMIT": 409,
    "BANK_ACCOUNT_EXISTS": 409,
    "VERIFICATION_EXPIRED_OR_LOCKED": 409,
    "HOLD_EXPIRED_OR_ALREADY_PAID": 409,
    "BOOKING_RULE_VIOLATION": 422,
    "BANK_ACCOUNT_NOT_VERIFIED": 422,
    "PAYMENT_FAILED": 502,
}
# Reasons that share the generic INVALID_INPUT code but need their own message.
INVALID_INPUT_REASONS = {
    "INVALID_INPUT": "INVALID_BOOKING_INPUT",
    "INVALID_BANK_ACCOUNT_INPUT": "INVALID_BANK_ACCOUNT_INPUT",
}


def api_error(code: str, message_key: str | None = None, context=None):
    message = user_message(message_key or code, context)
    return jsonify({"code": code, "message": message}), ERROR_STATUSES[code]


def error_response(error: BookingError):
    if error.reason in INVALID_INPUT_REASONS:
        return api_error("INVALID_INPUT", INVALID_INPUT_REASONS[error.reason])
    return api_error(error.code, error.reason, error.context)


def api_user():
    """Return (user, None) for a logged-in User, or (None, error response)."""
    current_user = session.get("user")
    if not current_user:
        return None, api_error("UNAUTHENTICATED")
    if current_user.get("role") != "USER":
        return None, api_error("FORBIDDEN")
    return current_user, None


def _forbidden_page(current_user):
    return (
        render_template(
            "pages/forbidden.html",
            default_url=default_url_for_role(current_user["role"]),
        ),
        403,
    )


def _payment_step(current_user, booking_id: str):
    with closing(get_db_connection(current_app.config["DATABASE_PATH"])) as connection:
        booking = connection.execute(
            """
            SELECT Booking.BookingID, Booking.UserID, Booking.BookingDate,
                   Booking.StartTime, Booking.EndTime, Booking.Status,
                   Booking.HoldExpiresAt, Booking.DepositAmount,
                   Court.CourtName, Court.Location
            FROM Booking JOIN Court ON Court.CourtID = Booking.CourtID
            WHERE Booking.BookingID = ?
            """,
            (booking_id,),
        ).fetchone()

    seconds_left = 0
    if booking and booking["UserID"] == current_user["user_id"] and booking["Status"] == "PENDING":
        hold_expires_at = datetime.strptime(booking["HoldExpiresAt"], DATETIME_FORMAT)
        seconds_left = max(0, int((hold_expires_at - datetime.now()).total_seconds()))

    if not booking or booking["UserID"] != current_user["user_id"] or seconds_left == 0:
        return render_template("pages/payment_unavailable.html")

    return render_template(
        "pages/payment.html",
        booking=booking,
        seconds_left=seconds_left,
        banks=bank_gateway.SUPPORTED_BANKS,
    )


@bookings_bp.get("/book")
def book():
    current_user = session.get("user")
    if current_user and current_user.get("role") != "USER":
        return _forbidden_page(current_user)

    booking_id = request.args.get("bookingId", "")
    if booking_id:
        if not current_user:
            return redirect(url_for("auth.login", next=request.full_path.removesuffix("?")))
        return _payment_step(current_user, booking_id)

    with closing(get_db_connection(current_app.config["DATABASE_PATH"])) as connection:
        courts = connection.execute(
            """
            SELECT CourtID, CourtName, Location, PricePerHour, OpenTime, CloseTime
            FROM Court WHERE Status = 'ACTIVE' ORDER BY CourtID
            """
        ).fetchall()

    selection = {
        "court_id": request.args.get("courtId", ""),
        "date": request.args.get("date", ""),
        "start_time": request.args.get("startTime", ""),
        "end_time": request.args.get("endTime", ""),
    }
    return render_template(
        "pages/book.html",
        courts=courts,
        selection=selection,
        today=date.today().isoformat(),
        restored=request.args.get("restored") == "1" and current_user is not None,
    )


@bookings_bp.post("/api/bookings")
def api_create_booking():
    current_user, error = api_user()
    if error:
        return error

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return api_error("INVALID_INPUT", "INVALID_BOOKING_INPUT")

    try:
        booking = create_booking(
            current_app.config["DATABASE_PATH"],
            current_user["user_id"],
            payload.get("courtId"),
            payload.get("bookingDate"),
            payload.get("startTime"),
            payload.get("endTime"),
        )
    except BookingError as booking_error:
        return error_response(booking_error)

    return jsonify(booking), 201


@bookings_bp.post("/api/bookings/<int:booking_id>/payment")
def api_pay_booking(booking_id: int):
    current_user, error = api_user()
    if error:
        return error

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}

    try:
        payment = pay_booking(
            current_app.config["DATABASE_PATH"],
            current_user["user_id"],
            booking_id,
            payload.get("bankAccountId"),
        )
    except BookingError as booking_error:
        return error_response(booking_error)

    return jsonify(payment), 200
