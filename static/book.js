(() => {
  const form = document.getElementById("book-form");
  if (!form) return;

  const STEP_MINUTES = 30;
  const MIN_DURATION = 60;
  const courtSelect = document.getElementById("court");
  const dateInput = document.getElementById("booking-date");
  const startSelect = document.getElementById("start-time");
  const endSelect = document.getElementById("end-time");
  const scheduleState = document.getElementById("booking-schedule-state");
  const scheduleGrid = document.getElementById("booking-schedule-grid");
  const submitButton = document.getElementById("book-submit");
  const errorBox = document.getElementById("book-error");
  let scheduleRequest = 0;
  let scheduleSelection = null;

  const toMinutes = (value) => {
    const [hours, minutes] = value.split(":").map(Number);
    return hours * 60 + minutes;
  };
  const toTime = (total) =>
    `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
  const formatMoney = (amount) => `${Number(amount).toLocaleString("vi-VN")}đ`;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

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

  function refreshStartTimes(preferred, minimumDuration = MIN_DURATION) {
    const court = selectedCourt();
    fillOptions(startSelect, court.open, court.close - minimumDuration, preferred || startSelect.value);
  }

  function refreshEndTimes(preferred, minimumDuration = MIN_DURATION) {
    const court = selectedCourt();
    const start = toMinutes(startSelect.value);
    const previous = preferred || endSelect.value;
    fillOptions(endSelect, start + minimumDuration, court.close, previous);
  }

  function refreshSummary() {
    const court = selectedCourt();
    const hasTimes = Boolean(startSelect.value && endSelect.value);
    const duration = hasTimes
      ? toMinutes(endSelect.value) - toMinutes(startSelect.value)
      : 0;
    document.getElementById("summary-hours").textContent = `${court.openLabel} – ${court.closeLabel}`;
    document.getElementById("summary-duration").textContent =
      `${Math.floor(duration / 60)} giờ${duration % 60 ? ` ${duration % 60} phút` : ""}`;
    document.getElementById("summary-total").textContent = formatMoney(
      Math.round((court.price * duration) / 60),
    );
    const meetsMinimumDuration = hasTimes && duration >= MIN_DURATION;
    endSelect.setCustomValidity(
      meetsMinimumDuration ? "" : "Mỗi lượt đặt sân cần tối thiểu 1 giờ.",
    );
    submitButton.disabled = !meetsMinimumDuration;
  }

  function syncScheduleSelectionFromControls() {
    if (!startSelect.value || !endSelect.value) {
      scheduleSelection = null;
      return;
    }
    scheduleSelection = {
      courtId: courtSelect.value,
      start: toMinutes(startSelect.value),
      end: toMinutes(endSelect.value),
    };
  }

  function updateScheduleSelection() {
    if (!scheduleGrid) return;
    if (!startSelect.value || !endSelect.value) {
      for (const slot of scheduleGrid.querySelectorAll("[data-slot-start]")) {
        slot.classList.remove("is-selected");
      }
      return;
    }
    const selectionStart = toMinutes(startSelect.value);
    const selectionEnd = toMinutes(endSelect.value);
    for (const slot of scheduleGrid.querySelectorAll("[data-slot-start]")) {
      const slotStart = toMinutes(slot.dataset.slotStart);
      slot.classList.toggle(
        "is-selected",
        slot.dataset.courtId === courtSelect.value
          && slotStart >= selectionStart
          && slotStart < selectionEnd
          && slot.classList.contains("slot-available"),
      );
    }
  }

  function chooseScheduleSlot(courtId, slot) {
    const clickedStart = toMinutes(slot.startTime);
    const clickedEnd = clickedStart + STEP_MINUTES;
    let selection = { courtId, start: clickedStart, end: clickedEnd };

    if (scheduleSelection && scheduleSelection.courtId === courtId) {
      const { start, end } = scheduleSelection;
      if (clickedStart >= start && clickedStart < end) {
        if (end - start <= STEP_MINUTES) {
          scheduleSelection = null;
          startSelect.replaceChildren();
          endSelect.replaceChildren();
          refreshSummary();
          updateScheduleSelection();
          return;
        }
        if (clickedStart === start) {
          selection = { courtId, start: start + STEP_MINUTES, end };
        } else if (clickedEnd === end) {
          selection = { courtId, start, end: end - STEP_MINUTES };
        } else {
          selection = { courtId, start, end: clickedStart };
        }
      } else if (clickedStart === end) {
        selection = { courtId, start, end: clickedEnd };
      } else if (clickedEnd === start) {
        selection = { courtId, start: clickedStart, end };
      }
    }

    scheduleSelection = selection;
    courtSelect.value = String(courtId);
    refreshStartTimes(toTime(selection.start), STEP_MINUTES);
    startSelect.value = toTime(selection.start);
    refreshEndTimes(toTime(selection.end), STEP_MINUTES);
    refreshSummary();
    updateScheduleSelection();
  }

  function renderSchedule(courts, startTimes) {
    const columns = `minmax(150px, 1.4fr) repeat(${startTimes.length}, minmax(64px, 1fr))`;
    const header = element("div", "booking-schedule-header");
    header.style.gridTemplateColumns = columns;
    header.append(element("span", "booking-schedule-court-label", "Sân"));
    for (const startTime of startTimes) {
      header.append(element("span", "booking-schedule-time-label", startTime));
    }

    const rows = courts.map(({ court, slots }, courtIndex) => {
      const row = element("div", "booking-schedule-row");
      row.style.gridTemplateColumns = columns;
      row.append(element("span", "booking-schedule-court-label", `Sân ${courtIndex + 1}`));
      const slotsByStart = new Map(slots.map((slot) => [slot.startTime, slot]));

      for (const [index, startTime] of startTimes.entries()) {
        const slot = slotsByStart.get(startTime);
        if (!slot) {
          row.append(element("span", "schedule-slot slot-outside"));
          continue;
        }

        const status = slot.status.toLowerCase();
        if (slot.available) {
          const button = element("button", `schedule-slot slot-${status}`, startTime);
          button.type = "button";
          button.dataset.courtId = String(court.id);
          button.dataset.slotStart = startTime;
          button.setAttribute(
            "aria-label",
            `${court.name}, ${startTime}–${slot.endTime}, còn trống, chọn khung giờ`,
          );
          button.addEventListener("click", () => chooseScheduleSlot(court.id, slot));
          row.append(button);
        } else {
          const statusLabel = slot.status === "BOOKED" ? "Đã đặt" : "Không thể đặt";
          const cell = element("span", `schedule-slot slot-${status}`);
          cell.setAttribute("aria-label", `${court.name}, ${startTime}–${slot.endTime}: ${statusLabel}`);
          cell.title = `${startTime}–${slot.endTime}: ${statusLabel}`;
          row.append(cell);
        }
      }
      return row;
    });

    scheduleGrid.replaceChildren(header, ...rows);
    updateScheduleSelection();
  }

  async function loadSchedule() {
    const requestId = ++scheduleRequest;
    scheduleState.hidden = false;
    scheduleState.className = "booking-schedule-state is-loading";
    scheduleState.textContent = "Đang tải lịch sân...";
    scheduleGrid.replaceChildren();

    const courts = [...courtSelect.options].map((option) => ({
      id: option.value,
      name: option.dataset.name,
    }));
    const query = new URLSearchParams({
      date: dateInput.value,
      slotDuration: String(STEP_MINUTES),
    });

    try {
      const availability = await Promise.all(courts.map(async (court) => {
        const availabilityUrl = form.dataset.availabilityUrl.replace(
          "/0/availability",
          `/${court.id}/availability`,
        );
        const result = await apiRequest("GET", `${availabilityUrl}?${query}`);
        return { court, slots: result.slots };
      }));
      if (requestId !== scheduleRequest) return;

      const startTimes = [...new Set(availability.flatMap(({ slots }) =>
        slots.map((slot) => slot.startTime),
      ))].sort((left, right) => toMinutes(left) - toMinutes(right));
      if (startTimes.length === 0) {
        scheduleState.className = "booking-schedule-state";
        scheduleState.textContent = "Không có khung giờ đặt được trong ngày này.";
        return;
      }

      renderSchedule(availability, startTimes);
      scheduleState.hidden = true;
    } catch (error) {
      if (requestId !== scheduleRequest) return;
      scheduleState.className = "booking-schedule-state is-error";
      scheduleState.textContent = error.message;
    }
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
    syncScheduleSelectionFromControls();
    updateScheduleSelection();
  });
  startSelect.addEventListener("change", () => {
    refreshEndTimes();
    refreshSummary();
    syncScheduleSelectionFromControls();
    updateScheduleSelection();
  });
  endSelect.addEventListener("change", () => {
    refreshSummary();
    syncScheduleSelectionFromControls();
    updateScheduleSelection();
  });
  dateInput.addEventListener("change", loadSchedule);

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
      submitButton.disabled =
        toMinutes(endSelect.value) - toMinutes(startSelect.value) < MIN_DURATION;
      submitButton.textContent = "Xác nhận đặt sân";
    }
  });

  refreshStartTimes(startSelect.dataset.initial);
  refreshEndTimes(endSelect.dataset.initial);
  refreshSummary();
  syncScheduleSelectionFromControls();
  loadSchedule();
})();
