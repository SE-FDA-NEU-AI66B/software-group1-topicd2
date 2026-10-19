// Shared helper for calling SmashGo JSON APIs. Error responses follow
// { code, message } (docs/design.md section 3), so callers can show
// `error.message` to the user and branch on `error.code`.
class ApiError extends Error {
  constructor(code, message, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function apiRequest(method, url, body) {
  const options = {
    method,
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(url, options);
  } catch {
    throw new ApiError(
      "NETWORK_ERROR",
      "Không kết nối được tới máy chủ. Hãy kiểm tra mạng và thử lại.",
      0,
    );
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      data?.code || "UNEXPECTED_ERROR",
      data?.message || "Yêu cầu chưa thể xử lý do có lỗi ngoài dự kiến. Vui lòng thử lại sau.",
      response.status,
    );
  }
  return data;
}
