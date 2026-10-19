ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": (
        "Email hoặc mật khẩu chưa đúng. Hãy kiểm tra lại cả hai, "
        "hoặc tạo tài khoản nếu bạn chưa có."
    ),
    "EMAIL_EXISTS": (
        "Email này đã được đăng ký. Hãy đăng nhập, "
        "hoặc dùng một email khác để đăng ký."
    ),
    "INVALID_INPUT": (
        "Một số thông tin còn thiếu hoặc chưa hợp lệ. Họ tên không được để trống, "
        "email phải có dạng ten@vidu.com, mật khẩu cần ít nhất 8 ký tự."
    ),
    "INVALID_BOOKING_INPUT": (
        "Thông tin đặt sân chưa hợp lệ. Hãy chọn sân, ngày, giờ bắt đầu và giờ "
        "kết thúc theo bước 30 phút."
    ),
    "UNAUTHENTICATED": "Bạn cần đăng nhập để đặt sân.",
    "FORBIDDEN": "Chỉ tài khoản người chơi mới có thể đặt sân.",
    "COURT_NOT_FOUND": (
        "Sân này không tồn tại hoặc đang tạm ngừng nhận đặt. Hãy chọn sân khác."
    ),
    "SLOT_UNAVAILABLE": (
        "{court_name} đã có lịch trong khung {start_time}–{end_time}. "
        "Hãy chọn khung giờ khác hoặc sân khác."
    ),
    "BOOKING_TOO_SHORT": "Mỗi lượt đặt sân cần dài ít nhất 1 giờ.",
    "BOOKING_GAP": (
        "Khung giờ này để trống {gap_minutes} phút so với lượt đặt "
        "{start_time}–{end_time}. Hãy đặt nối liền với lượt đó, hoặc cách ra "
        "ít nhất 1 giờ."
    ),
    "OUTSIDE_OPENING_HOURS": (
        "Sân chỉ mở cửa từ {open_time} đến {close_time}. Hãy chọn giờ trong "
        "khoảng này."
    ),
    "BOOKING_IN_PAST": "Không thể đặt khung giờ đã qua. Hãy chọn thời điểm sau hiện tại.",
    "ACTIVE_BOOKING_LIMIT": (
        "Bạn đang có {limit} lượt đặt sắp tới. Hãy chơi xong hoặc hủy một lượt "
        "trước khi đặt thêm."
    ),
}

FALLBACK_MESSAGE = (
    "Yêu cầu chưa thể xử lý do có lỗi ngoài dự kiến. "
    "Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ."
)


def user_message(code: str, context: dict | None = None) -> str:
    message = ERROR_MESSAGES.get(code)
    if message is None:
        return FALLBACK_MESSAGE
    try:
        return message.format(**(context or {}))
    except (KeyError, IndexError):
        return FALLBACK_MESSAGE