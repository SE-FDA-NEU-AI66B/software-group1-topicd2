// Task #94: Render review requests and all courts, then submit Admin decisions through the protected APIs.
(() => {
  const root = document.getElementById("admin-courts");
  if (!root) return;

  const requestList = document.getElementById("request-list");
  const requestState = document.getElementById("requests-state");
  const courtList = document.getElementById("court-list");
  const courtState = document.getElementById("courts-state");
  const notice = document.getElementById("admin-notice");
  const dialog = document.getElementById("reject-dialog");
  const rejectForm = document.getElementById("reject-form");
  const rejectReason = document.getElementById("reject-reason");
  const rejectError = document.getElementById("reject-error");
  const rejectConfirm = document.getElementById("reject-confirm");
  let rejectingRequest = null;

  // Task #94: Create text-only DOM elements so court data is never interpreted as HTML.
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // Task #94: Format prices consistently with the Vietnamese-facing application.
  function formatMoney(amount) {
    return `${Number(amount).toLocaleString("vi-VN")}đ`;
  }

  // Task #94: Display request photos and details before the Admin makes a decision.
  function renderRequest(request) {
    const item = element("li", "admin-request");
    const details = element("div", "admin-request-details");
    const title = element("h3", "", request.courtName);
    const manager = element("p", "", `Đề xuất bởi ${request.managerName}`);
    const location = element("p", "", request.location);
    const description = element("p", "admin-description", request.description || "Chưa có mô tả.");
    const schedule = element(
      "p",
      "",
      `${request.openTime}–${request.closeTime} · ${formatMoney(request.pricePerHour)} / giờ`,
    );
    details.append(title, manager, location, description, schedule);

    const gallery = element("div", "admin-gallery");
    (request.images || []).forEach((image) => {
      const photo = document.createElement("img");
      photo.src = image.url;
      photo.alt = `Ảnh ${request.courtName}`;
      photo.loading = "lazy";
      gallery.append(photo);
    });
    if (gallery.childElementCount) details.append(gallery);

    const actions = element("div", "admin-actions");
    const approve = element("button", "primary-button", "Duyệt");
    approve.type = "button";
    approve.addEventListener("click", () => reviewRequest(request, "APPROVED"));
    const reject = element("button", "danger-button", "Từ chối");
    reject.type = "button";
    reject.addEventListener("click", () => openRejectDialog(request));
    actions.append(approve, reject);
    item.append(details, actions);
    return item;
  }

  // Task #94: Show every court status, upcoming-booking count and the corresponding status action.
  function renderCourt(court) {
    const row = document.createElement("tr");
    const courtCell = element("td", "", court.courtName);
    courtCell.append(element("span", "admin-subtext", court.location));
    const managerCell = element("td", "", court.managerName);
    const priceCell = element("td", "", `${formatMoney(court.pricePerHour)} / giờ`);
    const bookingsCell = element("td", "", String(court.upcomingBookings));
    const statusCell = element("td");
    statusCell.append(element("span", `admin-status status-${court.status.toLowerCase()}`, court.status));
    const actionCell = element("td");

    if (court.status === "ACTIVE") {
      const disable = element("button", "danger-button", "Tạm ngưng");
      disable.type = "button";
      disable.addEventListener("click", () => updateCourtStatus(court, "DISABLED"));
      actionCell.append(disable);
    } else {
      const activate = element("button", "primary-button", "Kích hoạt");
      activate.type = "button";
      activate.addEventListener("click", () => updateCourtStatus(court, "ACTIVE"));
      actionCell.append(activate);
    }
    row.append(courtCell, managerCell, priceCell, bookingsCell, statusCell, actionCell);
    return row;
  }

  // Task #94: Fetch pending review requests and present empty/error states explicitly.
  async function loadRequests() {
    requestState.textContent = "Đang tải yêu cầu...";
    requestList.replaceChildren();
    try {
      const requests = await apiRequest("GET", "/api/admin/court-requests");
      requestState.hidden = requests.length > 0;
      requestState.textContent = requests.length ? "" : "Hiện không có yêu cầu chờ duyệt.";
      requestList.replaceChildren(...requests.map(renderRequest));
    } catch (error) {
      requestState.hidden = false;
      requestState.textContent = error.message;
    }
  }

  // Task #94: Fetch all courts, including disabled courts, and expose API conflicts to the Admin.
  async function loadCourts() {
    courtState.textContent = "Đang tải danh sách sân...";
    courtList.replaceChildren();
    try {
      const courts = await apiRequest("GET", "/api/admin/courts");
      courtState.hidden = courts.length > 0;
      courtState.textContent = courts.length ? "" : "Chưa có sân nào.";
      courtList.replaceChildren(...courts.map(renderCourt));
    } catch (error) {
      courtState.hidden = false;
      courtState.textContent = error.message;
    }
  }

  // Task #94: Submit approval or rejection and refresh both the request queue and court list.
  async function reviewRequest(request, decision, reason) {
    try {
      await apiRequest("POST", `/api/admin/court-requests/${request.requestId}/review`, {
        decision,
        ...(reason ? { rejectReason: reason } : {}),
      });
      dialog.close();
      notice.textContent = decision === "APPROVED"
        ? `Đã duyệt yêu cầu “${request.courtName}”.`
        : `Đã từ chối yêu cầu “${request.courtName}”.`;
      notice.hidden = false;
      await Promise.all([loadRequests(), loadCourts()]);
    } catch (error) {
      if (dialog.open) {
        rejectError.textContent = error.message;
        rejectError.hidden = false;
      } else {
        notice.textContent = error.message;
        notice.hidden = false;
      }
    }
  }

  // Task #94: Require a written reason in the rejection dialog before sending the decision.
  function openRejectDialog(request) {
    rejectingRequest = request;
    rejectReason.value = "";
    rejectError.hidden = true;
    document.getElementById("reject-summary").textContent =
      `${request.courtName} · ${request.managerName}`;
    dialog.showModal();
    rejectReason.focus();
  }

  // Task #94: Call the guarded status API and retain the server's upcoming-booking conflict message.
  async function updateCourtStatus(court, status) {
    try {
      await apiRequest("PATCH", `/api/admin/courts/${court.courtId}/status`, { status });
      notice.textContent = `Đã cập nhật trạng thái sân “${court.courtName}”.`;
      notice.hidden = false;
      await loadCourts();
    } catch (error) {
      notice.textContent = error.message;
      notice.hidden = false;
    }
  }

  document.getElementById("reload-requests").addEventListener("click", loadRequests);
  document.getElementById("reload-courts").addEventListener("click", loadCourts);
  document.getElementById("reject-cancel").addEventListener("click", () => dialog.close());
  rejectForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const reason = rejectReason.value.trim();
    if (!reason || !rejectingRequest) {
      rejectError.textContent = "Vui lòng nhập lý do từ chối.";
      rejectError.hidden = false;
      return;
    }
    rejectConfirm.disabled = true;
    try {
      await reviewRequest(rejectingRequest, "REJECTED", reason);
    } finally {
      rejectConfirm.disabled = false;
    }
  });

  // Task #94: Load both Admin panels when the page is ready.
  Promise.all([loadRequests(), loadCourts()]);
})();
