// Task #95: Load court availability by date and let users carry a free slot into the booking form.
(() => {
  const root = document.getElementById("court-detail");
  if (!root) return;

  const dateInput = document.getElementById("availability-date");
  const state = document.getElementById("availability-state");
  const slotsList = document.getElementById("availability-slots");

  // Task #95: Build DOM nodes with textContent so API values are not parsed as HTML.
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // Task #95: Build booking URLs with the chosen court, date and complete slot.
  function bookingUrl(slot) {
    const query = new URLSearchParams({
      courtId: root.dataset.courtId,
      date: dateInput.value,
      startTime: slot.startTime,
      endTime: slot.endTime,
    });
    return `${root.dataset.bookUrl}?${query}`;
  }

  // Task #95: Render available slots as booking links and unavailable slots as status-only items.
  function renderSlot(slot) {
    const item = element("li", `availability-slot slot-${slot.status.toLowerCase()}`);
    const label = `${slot.startTime}–${slot.endTime}`;
    if (slot.available) {
      const link = element("a", "", `${label} · Đặt sân`);
      link.href = bookingUrl(slot);
      item.append(link);
    } else {
      item.append(element("span", "", `${label} · ${
        slot.status === "BOOKED"
          ? "Đã có lịch"
          : "Không thể đặt"
      }`));
    }
    return item;
  }

  // Task #95: Expose loading, empty and error states while fetching the selected day's availability.
  async function loadAvailability() {
    state.hidden = false;
    state.className = "availability-state is-loading";
    state.replaceChildren(element("span", "state-loading-indicator"));
    state.append(document.createTextNode("Đang tải lịch trống..."));
    slotsList.replaceChildren();

    try {
      const query = new URLSearchParams({ date: dateInput.value });
      const result = await apiRequest(
        "GET",
        `${root.dataset.availabilityUrl}?${query}`,
      );
      slotsList.replaceChildren(...result.slots.map(renderSlot));
      if (result.slots.length === 0) {
        state.textContent = "Sân không có khung giờ đặt được trong ngày này.";
        return;
      }
      state.hidden = true;
    } catch (error) {
      state.className = "availability-state is-error";
      state.textContent = error.message;
    }
  }

  dateInput.addEventListener("change", loadAvailability);
  loadAvailability();
})();
