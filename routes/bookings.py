from contextlib import closing
from datetime import date

from flask import Blueprint, current_app, jsonify, render_template, request, session

from booking_service import BookingError, create_booking
from database import get_db_connection
from errors import user_message
from routes.auth import default_url_for_role

bookings_bp = Blueprint("bookings", __name__)


def api_error(code: str, status: int, message_key: str | None = None, context=None):
    message = user_message(message_key or code, context)
    return jsonify({"code": code, "message": message}), status


@bookings_bp.get("/book")
def book():
    current_user = session.get("user")
    if current_user and current_user.get("role") != "USER":
        return (
            render_template(
                "pages/forbidden.html",
                default_url=default_url_for_role(current_user["role"]),
            ),
            403,
        )

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
    current_user = session.get("user")
    if not current_user:
        return api_error("UNAUTHENTICATED", 401)
    if current_user.get("role") != "USER":
        return api_error("FORBIDDEN", 403)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return api_error("INVALID_INPUT", 400, "INVALID_BOOKING_INPUT")

    try:
        booking = create_booking(
            current_app.config["DATABASE_PATH"],
            current_user["user_id"],
            payload.get("courtId"),
            payload.get("bookingDate"),
            payload.get("startTime"),
            payload.get("endTime"),
        )
    except BookingError as error:
        statuses = {
            "INVALID_INPUT": 400,
            "COURT_NOT_FOUND": 404,
            "SLOT_UNAVAILABLE": 409,
            "ACTIVE_BOOKING_LIMIT": 409,
            "BOOKING_RULE_VIOLATION": 422,
        }
        message_key = "INVALID_BOOKING_INPUT" if error.code == "INVALID_INPUT" else error.reason
        return api_error(error.code, statuses[error.code], message_key, error.context)

    return jsonify(booking), 201
