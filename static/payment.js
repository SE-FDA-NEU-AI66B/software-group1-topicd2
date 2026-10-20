(() => {
  const root = document.getElementById("payment");
  if (!root) return;

  const bookingId = root.dataset.bookingId;
  const deadline = Date.now() + Number(root.dataset.secondsLeft) * 1000;
  const countdown = document.getElementById("hold-countdown");
  const errorBox = document.getElementById("payment-error");
  const noticeBox = document.getElementById("payment-notice");
  const accountsLoading = document.getElementById("accounts-loading");
  const accountsEmpty = document.getElementById("accounts-empty");
  const accountList = document.getElementById("account-list");
  const showLinkButton = document.getElementById("show-link-form");
  const hideLinkButton = document.getElementById("hide-link-form");
  const linkForm = document.getElementById("link-form");
  const otpForm = document.getElementById("otp-form");
  const payActions = document.getElementById("pay-actions");
  const payButton = document.getElementById("pay-button");
  const payOtpForm = document.getElementById("pay-otp-form");

  let pendingAccountId = null;
  let hasVerifiedAccount = false;
  let expired = false;

  function showError(message) {
    noticeBox.hidden = true;
    errorBox.textContent = message;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function showNotice(message) {
    errorBox.hidden = true;
    noticeBox.textContent = message;
    noticeBox.hidden = false;
  }

  function selectedAccountId() {
    const checked = accountList.querySelector("input[name=bankAccountId]:checked");
    return checked ? Number(checked.value) : null;
  }

  function refreshPayButton() {
    payButton.disabled = expired || selectedAccountId() === null;
  }

  function setBusy(button, busy, label) {
    button.disabled = busy;
    if (label) button.textContent = label;
  }

  // Once a verified account exists the link form stays hidden; the "+" button opens it.
  function showLinkSection(open) {
    linkForm.hidden = !open;
    otpForm.hidden = true;
    showLinkButton.hidden = !hasVerifiedAccount || open;
    hideLinkButton.hidden = !hasVerifiedAccount;
  }

  function closePaymentOtp() {
    payOtpForm.hidden = true;
    payActions.hidden = false;
  }

  function expireHold(showMessage = true) {
    expired = true;
    countdown.textContent = "00:00";
    root.querySelectorAll("button, input, select").forEach((element) => {
      element.disabled = true;
    });
    if (showMessage) {
      showError(
        "Đã hết 10 phút giữ chỗ nên khung giờ đã được nhả cho người khác. Hãy đặt lại từ trang đặt sân.",
      );
    }
  }

  function tick() {
    const remaining = Math.max(0, Math.round((deadline - Date.now()) / 1000));
    countdown.textContent = `${String(Math.floor(remaining / 60)).padStart(2, "0")}:${String(remaining % 60).padStart(2, "0")}`;
    if (remaining === 0) {
      expireHold();
      return;
    }
    window.setTimeout(tick, 1000);
  }

  function renderAccounts(accounts) {
    const previous = selectedAccountId();
    accountList.replaceChildren();
    accountsEmpty.hidden = accounts.length > 0;
    for (const account of accounts) {
      const label = document.createElement("label");
      label.className = "account-option";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "bankAccountId";
      input.value = account.bankAccountId;
      input.disabled = !account.isVerified;
      // Default to the account linked first (the primary account).
      input.checked = previous !== null ? account.bankAccountId === previous : account.isPrimary;
      const text = document.createElement("span");
      text.textContent = `${account.bankName} •••• ${account.accountNumberLast4}`;
      const status = document.createElement("small");
      if (account.isPrimary) {
        status.className = "primary-badge";
        status.textContent = "Tài khoản chính";
      } else {
        status.textContent = account.isVerified ? "Đã xác minh" : "Chưa xác minh, liên kết lại để nhận OTP";
      }
      label.append(input, text, status);
      accountList.append(label);
    }
    hasVerifiedAccount = accounts.some((account) => account.isVerified);
    showLinkSection(!hasVerifiedAccount);
    refreshPayButton();
  }

  async function loadAccounts() {
    accountsLoading.hidden = false;
    try {
      renderAccounts(await apiRequest("GET", "/api/bank-accounts"));
    } catch (error) {
      showError(error.message);
    } finally {
      accountsLoading.hidden = true;
    }
  }

  async function sendPaymentOtp() {
    const bankAccountId = selectedAccountId();
    if (bankAccountId === null) return;
    const result = await apiRequest("POST", `/api/bookings/${bookingId}/payment/otp`, { bankAccountId });
    document.getElementById("pay-otp-hint").textContent =
      `Mã OTP đã được gửi tới tài khoản ${result.bankName} •••• ${result.accountNumberLast4}. Mã có hiệu lực 5 phút.`;
    payActions.hidden = true;
    payOtpForm.hidden = false;
    payOtpForm.otp.value = "";
    payOtpForm.otp.focus();
  }

  function handlePaymentError(error) {
    showError(error.message);
    if (error.code === "HOLD_EXPIRED_OR_ALREADY_PAID") {
      expireHold(false);
      return true;
    }
    return false;
  }

  accountList.addEventListener("change", () => {
    closePaymentOtp();
    refreshPayButton();
  });

  showLinkButton.addEventListener("click", () => {
    showLinkSection(true);
    document.getElementById("account-number").focus();
  });

  hideLinkButton.addEventListener("click", () => showLinkSection(false));

  linkForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!linkForm.reportValidity()) return;
    const button = linkForm.querySelector("button[type=submit]");
    setBusy(button, true, "Đang gửi mã...");
    try {
      const account = await apiRequest("POST", "/api/bank-accounts", {
        bankName: linkForm.bankName.value,
        accountNumber: linkForm.accountNumber.value,
        accountHolderName: linkForm.accountHolderName.value,
      });
      pendingAccountId = account.bankAccountId;
      linkForm.hidden = true;
      otpForm.hidden = false;
      document.getElementById("otp-hint").textContent =
        `Mã OTP đã được gửi cho tài khoản ${account.bankName} •••• ${account.accountNumberLast4}. Mã có hiệu lực 5 phút.`;
      otpForm.otp.value = "";
      otpForm.otp.focus();
    } catch (error) {
      showError(error.message);
    } finally {
      setBusy(button, expired, "Gửi mã OTP");
    }
  });

  otpForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!otpForm.reportValidity()) return;
    const button = otpForm.querySelector("button");
    setBusy(button, true, "Đang xác minh...");
    try {
      await apiRequest("POST", `/api/bank-accounts/${pendingAccountId}/verify`, {
        otp: otpForm.otp.value,
      });
      linkForm.reset();
      showNotice("Tài khoản đã được xác minh và thêm vào danh sách.");
      await loadAccounts();
    } catch (error) {
      showError(error.message);
      if (error.code === "VERIFICATION_EXPIRED_OR_LOCKED") {
        loadAccounts().then(() => showLinkSection(true));
      }
    } finally {
      setBusy(button, expired, "Xác minh");
    }
  });

  payButton.addEventListener("click", async () => {
    setBusy(payButton, true, "Đang gửi mã...");
    try {
      await sendPaymentOtp();
    } catch (error) {
      if (handlePaymentError(error)) return;
    }
    setBusy(payButton, false, "Thanh toán");
    refreshPayButton();
  });

  document.getElementById("resend-pay-otp").addEventListener("click", async () => {
    try {
      await sendPaymentOtp();
      showNotice("Đã gửi mã OTP mới.");
    } catch (error) {
      handlePaymentError(error);
    }
  });

  payOtpForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!payOtpForm.reportValidity()) return;
    const button = payOtpForm.querySelector("button[type=submit]");
    setBusy(button, true, "Đang thanh toán...");
    try {
      await apiRequest("POST", `/api/bookings/${bookingId}/payment`, {
        bankAccountId: selectedAccountId(),
        paymentMethod: "BANK_TRANSFER",
        otp: payOtpForm.otp.value,
      });
      window.location.assign(root.dataset.successUrl);
      return;
    } catch (error) {
      if (handlePaymentError(error)) return;
      // A failed charge uses up the OTP; the user starts again from "Thanh toán".
      if (error.code === "PAYMENT_FAILED") closePaymentOtp();
    }
    setBusy(button, false, "Xác nhận thanh toán");
  });

  tick();
  loadAccounts();
})();
