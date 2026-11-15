
from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from booking_service import BookingError
from court_service import (
    get_active_court,
    get_court_availability,
    get_court_images,
    list_active_courts,
)

court_pages_bp = Blueprint("court_pages", __name__)


# Task #95: Return public court-page errors as clear JSON for availability clients.
def availability_error(error: BookingError):
    status = {
        "COURT_NOT_FOUND": 404,
        "INVALID_AVAILABILITY_DATE": 400,
        "INVALID_AVAILABILITY_DURATION": 400,
        "INVALID_COURT_FILTER": 400,
    }[error.reason]
    message = {
        "COURT_NOT_FOUND": "Không tìm thấy sân đang hoạt động.",
        "INVALID_AVAILABILITY_DATE": "Ngày xem lịch không hợp lệ.",
        "INVALID_AVAILABILITY_DURATION": "Độ dài khung giờ không hợp lệ.",
        "INVALID_COURT_FILTER": (
            "Bộ lọc ngày và giờ không hợp lệ; khung giờ cần tối thiểu một giờ."
        ),
    }[error.reason]
    return jsonify({"code": error.reason, "message": message}), status


# Task #95: Expose the same location and date/time filters as the public HTML court listing.
@court_pages_bp.get("/api/courts")
def api_list_courts():
    try:
        courts = list_active_courts(
            current_app.config["DATABASE_PATH"],
            request.args.get("date", ""),
            request.args.get("startTime", ""),
            request.args.get("endTime", ""),
            request.args.get("location", ""),
        )
    except BookingError as error:
        return availability_error(error)
    images_by_court = get_court_images(
        current_app.config["DATABASE_PATH"],
        [court["CourtID"] for court in courts],
    )
    return jsonify(
        [
            {
                "courtId": court["CourtID"],
                "courtName": court["CourtName"],
                "location": court["Location"],
                "description": court["Description"],
                "pricePerHour": court["PricePerHour"],
                "openTime": court["OpenTime"],
                "closeTime": court["CloseTime"],
                "images": images_by_court[court["CourtID"]],
            }
            for court in courts
        ]
    )


# The court detail page was merged into /book, which shows the court's photos,
# address, description, price and hours next to its schedule. Old links still work.
@court_pages_bp.get("/courts/<int:court_id>")
def court_detail(court_id: int):
    if get_active_court(current_app.config["DATABASE_PATH"], court_id) is None:
        return render_template("pages/court_not_found.html"), 404
    return redirect(url_for("bookings.book", courtId=court_id))


# Task #95: Expose a public availability API with explicit loading/error-friendly JSON responses.
@court_pages_bp.get("/api/courts/<int:court_id>/availability")
def api_court_availability(court_id: int):
    try:
        slot_duration = int(request.args.get("slotDuration", "60"))
        result = get_court_availability(
            current_app.config["DATABASE_PATH"],
            court_id,
            request.args.get("date", ""),
            slot_duration,
        )
    except ValueError:
        return availability_error(BookingError("INVALID_AVAILABILITY_DURATION"))
    except BookingError as error:
        return availability_error(error)
    return jsonify(result)


# Task #95: Expose the same public court details shown by the HTML detail page.
@court_pages_bp.get("/api/courts/<int:court_id>")
def api_court_detail(court_id: int):
    court = get_active_court(current_app.config["DATABASE_PATH"], court_id)
    if court is None:
        return availability_error(BookingError("COURT_NOT_FOUND"))
    return jsonify(court)
