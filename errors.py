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
}

FALLBACK_MESSAGE = (
    "Yêu cầu chưa thể xử lý do có lỗi ngoài dự kiến. "
    "Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ."
)


def user_message(code: str) -> str:
    return ERROR_MESSAGES.get(code, FALLBACK_MESSAGE)