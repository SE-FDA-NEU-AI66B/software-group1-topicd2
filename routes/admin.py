from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

# Task #94: Route protected Admin court-management requests to the Admin service layer.
from admin_service import (
    list_admin_courts,
    list_court_requests,
    review_court_request,
    set_court_status,
)
from booking_service import BookingError

admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

# Task #94: Keep Admin endpoint errors consistent with HTTP semantics and Vietnamese UI messages.
ERROR_STATUSES = {
    "UNAUTHENTICATED": 401,
    "ADMIN_REQUIRED": 403,
    "COURT_NOT_FOUND": 404,
    "REQUEST_NOT_FOUND": 404,
    "INVALID_DECISION": 400,
    "INVALID_STATUS": 400,
    "INVALID_STATUS_FILTER": 400,
    "REQUEST_ALREADY_REVIEWED": 409,
    "REQUEST_TYPE_NOT_SUPPORTED": 409,
    "COURT_HAS_UPCOMING_BOOKINGS": 409,
}
ERROR_MESSAGES = {
    "UNAUTHENTICATED": "Bạn cần đăng nhập để thực hiện thao tác này.",
    "ADMIN_REQUIRED": "Chỉ quản trị viên mới có thể thực hiện thao tác này.",
    "COURT_NOT_FOUND": "Không tìm thấy sân.",
    "REQUEST_NOT_FOUND": "Không tìm thấy yêu cầu thêm sân.",
    "INVALID_DECISION": "Quyết định không hợp lệ; yêu cầu từ chối phải có lý do.",
    "INVALID_STATUS": "Trạng thái sân không hợp lệ.",
    "INVALID_STATUS_FILTER": "Bộ lọc trạng thái yêu cầu không hợp lệ.",
    "REQUEST_ALREADY_REVIEWED": "Yêu cầu này đã được xử lý.",
    "REQUEST_TYPE_NOT_SUPPORTED": "Loại yêu cầu này chưa được hỗ trợ.",
    "COURT_HAS_UPCOMING_BOOKINGS": (
        "Không thể tạm ngưng sân vì sân đang có lịch đặt sắp tới."
    ),
}


# Task #94: Enforce admin authorization for every JSON endpoint without redirecting API clients.
def admin_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        current_user = session.get("user")
        if not current_user:
            return api_error("UNAUTHENTICATED")
        if current_user.get("role") != "ADMIN":
            return api_error("ADMIN_REQUIRED")
        return view_function(*args, **kwargs)

    return wrapped


# Task #94: Keep admin API errors in the existing JSON code/message contract.
def api_error(code: str):
    return jsonify({"code": code, "message": ERROR_MESSAGES[code]}), ERROR_STATUSES[code]


# Task #94: Expose all court statuses for the Admin courts screen.
@admin_api_bp.get("/courts")
@admin_required
def api_admin_courts():
    return jsonify(list_admin_courts(current_app.config["DATABASE_PATH"]))


# Task #94: List review requests with a validated status filter and image details.
@admin_api_bp.get("/court-requests")
@admin_required
def api_admin_court_requests():
    try:
        requests_list = list_court_requests(
            current_app.config["DATABASE_PATH"], request.args.get("status", "PENDING")
        )
    except BookingError as error:
        return api_error(error.reason)
    return jsonify(requests_list)


# Task #94: Apply an Admin decision to a request using the logged-in Admin identity.
@admin_api_bp.post("/court-requests/<int:request_id>/review")
@admin_required
def api_review_court_request(request_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}
    try:
        result = review_court_request(
            current_app.config["DATABASE_PATH"],
            request_id,
            session["user"]["user_id"],
            payload.get("decision"),
            payload.get("rejectReason"),
        )
    except BookingError as error:
        return api_error(error.reason)
    return jsonify(result)


# Task #94: Validate and update court status, returning a conflict for occupied courts.
@admin_api_bp.patch("/courts/<int:court_id>/status")
@admin_required
def api_set_court_status(court_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}
    try:
        result = set_court_status(
            current_app.config["DATABASE_PATH"], court_id, payload.get("status")
        )
    except BookingError as error:
        return api_error(error.reason)
    return jsonify(result)
