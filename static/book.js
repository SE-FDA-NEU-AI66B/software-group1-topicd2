(() => {
  const form = document.getElementById("book-form");
  if (!form) return;

  const STEP_MINUTES = 30;
  const MIN_DURATION = 60;
  const courtSelect = document.getElementById("court");
  const dateInput = document.getElementById("booking-date");
  const startSelect = document.getElementById("start-time");
  const endSelect = document.getElementById("end-time");
  const submitButton = document.getElementById("book-submit");
  const errorBox = document.getElementById("book-error");

  const toMinutes = (value) => {
    const [hours, minutes] = value.split(":").map(Number);
    return hours * 60 + minutes;
  };
  const toTime = (total) =>
    `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
  const formatMoney = (amount) => `${Number(amount).toLocaleString("vi-VN")}đ`;

  function selectedCourt() {
    const option = courtSelect.selectedOptions[0];
    return {
      open: toMinutes(option.dataset.open),
      close: toMinutes(option.dataset.close),
      price: Number(option.dataset.price),
      openLabel: option.dataset.open,
      closeLabel: option.dataset.close,
    };
  }

  function fillOptions(select, from, to, preferred) {
    select.replaceChildren();
    for (let minute = from; minute <= to; minute += STEP_MINUTES) {
      select.add(new Option(toTime(minute), toTime(minute)));
    }
    if (preferred && [...select.options].some((option) => option.value === preferred)) {
      select.value = preferred;
    }
  }

  function refreshStartTimes(preferred) {
    const court = selectedCourt();
    fillOptions(startSelect, court.open, court.close - MIN_DURATION, preferred || startSelect.value);
  }

  function refreshEndTimes(preferred) {
    const court = selectedCourt();
    const start = toMinutes(startSelect.value);
    const previous = preferred || endSelect.value;
    fillOptions(endSelect, start + MIN_DURATION, court.close, previous);
  }

  function refreshSummary() {
    const court = selectedCourt();
    const duration = toMinutes(endSelect.value) - toMinutes(startSelect.value);
    document.getElementById("summary-hours").textContent = `${court.openLabel} – ${court.closeLabel}`;
    document.getElementById("summary-duration").textContent =
      `${Math.floor(duration / 60)} giờ${duration % 60 ? ` ${duration % 60} phút` : ""}`;
    document.getElementById("summary-total").textContent = formatMoney(
      Math.round((court.price * duration) / 60),
    );
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function currentSelection() {
    return {
      courtId: Number(courtSelect.value),
      bookingDate: dateInput.value,
      startTime: startSelect.value,
      endTime: endSelect.value,
    };
  }

  function redirectToLogin(selection) {
    const query = new URLSearchParams({
      courtId: selection.courtId,
      date: selection.bookingDate,
      startTime: selection.startTime,
      endTime: selection.endTime,
      restored: "1",
    });
    const next = `${form.dataset.bookUrl}?${query}`;
    window.location.assign(`${form.dataset.loginUrl}?${new URLSearchParams({ next })}`);
  }

  courtSelect.addEventListener("change", () => {
    refreshStartTimes();
    refreshEndTimes();
    refreshSummary();
  });
  startSelect.addEventListener("change", () => {
    refreshEndTimes();
    refreshSummary();
  });
  endSelect.addEventListener("change", refreshSummary);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    if (!form.reportValidity()) return;

    const selection = currentSelection();
    if (form.dataset.authenticated !== "true") {
      redirectToLogin(selection);
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Đang giữ chỗ...";
    try {
      const booking = await apiRequest("POST", "/api/bookings", selection);
      // Continue to the payment step while the 10-minute hold runs (BR3).
      window.location.assign(`${form.dataset.bookUrl}?bookingId=${booking.bookingId}`);
      return;
    } catch (error) {
      if (error.code === "UNAUTHENTICATED") {
        redirectToLogin(selection);
        return;
      }
      showError(error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Xác nhận đặt sân";
    }
  });

  refreshStartTimes(startSelect.dataset.initial);
  refreshEndTimes(endSelect.dataset.initial);
  refreshSummary();
})();
