(() => {
  const root = document.getElementById("my-bookings");
  if (!root) return;

  const STATUS_LABELS = {
    PENDING: "Chờ thanh toán",
    CONFIRMED: "Đã xác nhận",
    CHECKED_IN: "Đã nhận sân",
    COMPLETED: "Đã chơi",
    CANCELLED: "Đã hủy",
    EXPIRED: "Hết hạn giữ chỗ",
  };
  const list = document.getElementById("booking-list");
  const notice = document.getElementById("bookings-notice");
  const dialog = document.getElementById("cancel-dialog");
  const cancelForm = document.getElementById("cancel-form");
  const cancelError = document.getElementById("cancel-error");
  const cancelConfirm = document.getElementById("cancel-confirm");
  let cancelling = null;

  const formatMoney = (amount) => `${Number(amount).toLocaleString("vi-VN")}đ`;
  const formatDate = (isoDate) => isoDate.split("-").reverse().join("/");

  function showState(name) {
    root.querySelectorAll("[data-state]").forEach((element) => {
      element.hidden = element.dataset.state !== name;
    });
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function moneyLine(booking) {
    if (booking.status === "CANCELLED" && booking.paymentStatus) {
      return `Đã hoàn ${formatMoney(booking.refundAmount || 0)} / ${formatMoney(booking.paidAmount)}`;
    }
    if (booking.paymentStatus) return `Đã thanh toán ${formatMoney(booking.paidAmount)}`;
    return `Cần thanh toán ${formatMoney(booking.depositAmount)}`;
  }

  function renderBooking(booking) {
    const item = element("li", "booking-item");
    const info = element("div", "booking-info");
    info.append(
      element("strong", "", booking.courtName),
      element("span", "booking-when", `${booking.startTime}–${booking.endTime} · ${formatDate(booking.bookingDate)}`),
      element("span", "booking-money", moneyLine(booking)),
    );
    if (booking.status === "PENDING" && booking.holdExpiresAt) {
      info.append(element("span", "booking-hold", `Giữ chỗ đến ${booking.holdExpiresAt.slice(11, 16)}`));
    }

    const side = element("div", "booking-side");
    side.append(element("span", `booking-status status-${booking.status.toLowerCase()}`, STATUS_LABELS[booking.status] || booking.status));
    const actions = element("div", "booking-actions");
    if (booking.status === "PENDING") {
      const pay = element("a", "primary-link", "Thanh toán");
      pay.href = `${root.dataset.payUrl}?bookingId=${booking.bookingId}`;
      actions.append(pay);
    }
    if (booking.canCancel) {
      const cancel = element("button", "secondary-button", "Hủy lịch");
      cancel.type = "button";
      cancel.addEventListener("click", () => openCancelDialog(booking));
      actions.append(cancel);
    }
    side.append(actions);
    item.append(info, side);
    return item;
  }

  async function loadBookings() {
    showState("loading");
    try {
      const bookings = await apiRequest("GET", "/api/bookings/mine");
      if (bookings.length === 0) {
        showState("empty");
        return;
      }
      list.replaceChildren(...bookings.map(renderBooking));
      showState("data");
    } catch (error) {
      root.querySelector("[data-state=error] p").textContent = error.message;
      showState("error");
    }
  }

  function openCancelDialog(booking) {
    cancelling = booking;
    cancelError.hidden = true;
    cancelForm.cancelReason.value = "";
    document.getElementById("cancel-summary").textContent =
      `${booking.courtName}, ${booking.startTime}–${booking.endTime} ngày ${formatDate(booking.bookingDate)}.`;
    const refund = document.getElementById("cancel-refund");
    if (!booking.paymentStatus) {
      refund.textContent = "Lượt đặt chưa thanh toán nên không phát sinh hoàn tiền.";
    } else if (booking.refundIfCancelledNow === booking.paidAmount) {
      refund.textContent = `Nếu hủy bây giờ, bạn được hoàn đủ ${formatMoney(booking.paidAmount)}.`;
    } else {
      refund.textContent =
        `Đã trong vòng 4 giờ trước giờ chơi: bạn được hoàn ${formatMoney(booking.refundIfCancelledNow)} ` +
        `và mất ${formatMoney(booking.paidAmount - booking.refundIfCancelledNow)}.`;
    }
    dialog.showModal();
  }

  document.getElementById("cancel-dismiss").addEventListener("click", () => dialog.close());

  cancelForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    cancelConfirm.disabled = true;
    cancelConfirm.textContent = "Đang hủy...";
    try {
      const result = await apiRequest("DELETE", `/api/bookings/${cancelling.bookingId}`, {
        cancelReason: cancelForm.cancelReason.value,
      });
      dialog.close();
      notice.textContent = result.paymentStatus
        ? `Đã hủy lượt đặt. Số tiền hoàn lại: ${formatMoney(result.refundAmount)}.`
        : "Đã hủy lượt đặt.";
      notice.hidden = false;
      await loadBookings();
    } catch (error) {
      cancelError.textContent = error.message;
      cancelError.hidden = false;
    } finally {
      cancelConfirm.disabled = false;
      cancelConfirm.textContent = "Xác nhận hủy";
    }
  });

  loadBookings();
})();
