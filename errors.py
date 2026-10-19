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
    "INVALID_BANK_ACCOUNT_INPUT": (
        "Thông tin tài khoản chưa hợp lệ. Hãy chọn ngân hàng trong danh sách, nhập "
        "số tài khoản từ 6 đến 19 chữ số và tên chủ tài khoản."
    ),
    "BANK_ACCOUNT_EXISTS": (
        "Tài khoản này đã được liên kết và xác minh. Hãy chọn nó trong danh sách "
        "tài khoản của bạn."
    ),
    "BANK_ACCOUNT_NOT_FOUND": "Không tìm thấy tài khoản ngân hàng này. Hãy tải lại trang.",
    "NOT_ACCOUNT_OWNER": "Tài khoản ngân hàng này không thuộc về bạn.",
    "INVALID_OTP": "Mã OTP chưa đúng. Bạn còn {attempts_left} lần thử.",
    "VERIFICATION_EXPIRED_OR_LOCKED": (
        "Mã OTP đã hết hạn hoặc bạn đã nhập sai quá số lần cho phép. Hãy liên kết "
        "lại tài khoản để nhận mã mới."
    ),
    "BOOKING_NOT_FOUND": "Không tìm thấy lượt đặt này. Hãy kiểm tra lại lịch đặt của bạn.",
    "NOT_BOOKING_OWNER": "Lượt đặt này không thuộc về bạn.",
    "BOOKING_NOT_CANCELLABLE": (
        "Lượt đặt này không thể hủy vì đã bị hủy, đã hết hạn giữ chỗ, đã hoàn tất "
        "hoặc đã đến giờ chơi."
    ),
    "INVALID_STATUS_FILTER": "Bộ lọc trạng thái không hợp lệ.",
    "BANK_ACCOUNT_NOT_VERIFIED": (
        "Tài khoản chưa được xác minh. Hãy chọn một tài khoản đã xác minh, hoặc "
        "liên kết và nhập OTP trước khi thanh toán."
    ),
    "HOLD_EXPIRED_OR_ALREADY_PAID": (
        "Lượt đặt đã hết 10 phút giữ chỗ hoặc đã được thanh toán. Hãy kiểm tra lịch "
        "đặt của bạn hoặc đặt lại khung giờ khác."
    ),
    "PAYMENT_FAILED": (
        "Ngân hàng từ chối giao dịch, bạn chưa bị trừ tiền. Hãy thử lại hoặc chọn "
        "tài khoản khác trong thời gian giữ chỗ."
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