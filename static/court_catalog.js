// Task #95: Show an accessible loading message while the court filter form navigates.
(() => {
  const form = document.getElementById("court-search-form");
  if (!form) return;

  form.addEventListener("submit", () => {
    const submit = document.getElementById("court-search-submit");
    submit.disabled = true;
    submit.textContent = "Đang tìm...";
    document.getElementById("court-search-loading").hidden = false;
  });
})();
