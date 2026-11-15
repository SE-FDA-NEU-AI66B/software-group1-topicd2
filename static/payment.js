// Payment step of /book?bookingId=: a three-step flow like a bank transfer.
//   1. Account: the saved account is chosen by default; a first-time user (or
//      "+ Thêm tài khoản") types a new one.
//   2. OTP: the bank sends an OTP to the account and the user types it.
//   3. Confirm: the user reviews the payment and confirms it.
// A new account is linked in step 1 and paid with the OTP sent when it was
// linked, so the user enters one OTP; paying also saves it for next time.
(() => {
  const root = document.getElementById("payment");
  if (!root) return;

  const bookingId = root.dataset.bookingId;
  const deadline = Date.now() + Number(root.dataset.secondsLeft) * 1000;
  const countdown = document.getElementById("hold-countdown");
  const errorBox = document.getElementById("payment-error");
  const noticeBox = document.getElementById("payment-notice");

  const steps = {
    account: document.getElementById("step-account"),
    otp: document.getElementById("step-otp"),
    confirm: document.getElementById("step-confirm"),
  };
  const stepOrder = ["account", "otp", "confirm"];

  const accountsLoading = document.getElementById("accounts-loading");
  const savedAccounts = document.getElementById("saved-accounts");
  const accountList = document.getElementById("account-list");
  const newAccount = document.getElementById("new-account");
  const useSavedButton = document.getElementById("use-saved-account");
  const accountNext = document.getElementById("account-next");
  const otpSent = document.getElementById("otp-sent");
  const otpInput = document.getElementById("otp");
  const reviewAccount = document.getElementById("review-account");
  const confirmButton = document.getElementById("confirm-pay");

  let accounts = [];
  let addingAccount = false;
  // The account being paid with: { bankAccountId, label, isNew, details }.
  let payment = null;
  let expired = false;
  let paid = false;

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

  function clearMessages() {
    errorBox.hidden = true;
    noticeBox.hidden = true;
  }

  function setBusy(button, busy, label) {
    button.disabled = busy || expired;
    button.textContent = label;
  }

  function goTo(name) {
    const current = stepOrder.indexOf(name);
    stepOrder.forEach((step, index) => {
      steps[step].hidden = step !== name;
      const label = document.getElementById(`step-label-${step}`);
      label.classList.toggle("is-done", index < current);
      if (step === name) label.setAttribute("aria-current", "step");
      else label.removeAttribute("aria-current");
    });
  }

  function accountLabel(bankName, last4) {
    return `${bankName} •••• ${last4}`;
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

  // Returns true when the hold is gone and the page has been locked.
  function handleHoldError(error) {
    if (error.code !== "HOLD_EXPIRED_OR_ALREADY_PAID") return false;
    showError(error.message);
    expireHold(false);
    return true;
  }

  // ---- Step 1: account ----

  function selectedAccount() {
    const checked = accountList.querySelector("input[name=bankAccountId]:checked");
    return checked ? accounts.find((account) => account.bankAccountId === Number(checked.value)) : null;
  }

  // Show the saved accounts, or the form when there are none or the user is adding one.
  function showAccountChoice() {
    const hasSaved = accounts.length > 0;
    const typing = !hasSaved || addingAccount;
    savedAccounts.hidden = typing;
    newAccount.hidden = !typing;
    useSavedButton.hidden = !hasSaved;
    document.getElementById("new-account-title").textContent = hasSaved
      ? "Thêm tài khoản khác"
      : "Nhập tài khoản ngân hàng";
    newAccount.querySelectorAll("input, select").forEach((field) => {
      field.disabled = !typing || expired;
    });
    accountNext.disabled = expired;
  }

  function renderAccounts(selectId) {
    const previous = selectId ?? selectedAccount()?.bankAccountId ?? null;
    accountList.replaceChildren();
    for (const account of accounts) {
      const label = document.createElement("label");
      label.className = "account-option";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "bankAccountId";
      input.value = account.bankAccountId;
      // The saved primary account (the first one linked) is the default.
      input.checked = previous !== null ? account.bankAccountId === previous : account.isPrimary;
      const text = document.createElement("span");
      text.textContent = accountLabel(account.bankName, account.accountNumberLast4);
      const status = document.createElement("small");
      status.textContent = account.isPrimary ? "Tài khoản chính" : "Đã lưu";
      if (account.isPrimary) status.className = "primary-badge";
      label.append(input, text, status);
      accountList.append(label);
    }
    if (!selectedAccount() && accountList.querySelector("input")) {
      accountList.querySelector("input").checked = true;
    }
    showAccountChoice();
  }

  async function loadAccounts(selectId) {
    accountsLoading.hidden = false;
    accountNext.disabled = true;
    try {
      // Only verified accounts are saved; a half-linked one is simply typed again.
      accounts = (await apiRequest("GET", "/api/bank-accounts")).filter((account) => account.isVerified);
      if (selectId !== undefined) addingAccount = false;
      renderAccounts(selectId);
    } catch (error) {
      showError(error.message);
    } finally {
      accountsLoading.hidden = true;
    }
  }

  function otpSentMessage(label) {
    return `Ngân hàng đã gửi mã OTP tới số điện thoại đăng ký của tài khoản ${label}. Mã có hiệu lực 5 phút.`;
  }

  async function sendOtp() {
    if (payment.isNew) {
      // Linking again sends a new OTP to an account that is not verified yet.
      const linked = await apiRequest("POST", "/api/bank-accounts", payment.details);
      payment.bankAccountId = linked.bankAccountId;
    } else {
      await apiRequest("POST", `/api/bookings/${bookingId}/payment/otp`, {
        bankAccountId: payment.bankAccountId,
      });
    }
    otpSent.textContent = otpSentMessage(payment.label);
  }

  function openOtpStep() {
    otpInput.value = "";
    goTo("otp");
    otpInput.focus();
  }

  steps.account.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();
    if (newAccount.hidden) {
      const account = selectedAccount();
      if (!account) {
        showError("Hãy chọn một tài khoản để thanh toán.");
        return;
      }
      payment = {
        bankAccountId: account.bankAccountId,
        label: accountLabel(account.bankName, account.accountNumberLast4),
        isNew: false,
      };
    } else {
      const form = steps.account;
      if (![form.bankName, form.accountNumber, form.accountHolderName].every((field) => field.reportValidity())) {
        return;
      }
      const details = {
        bankName: form.bankName.value,
        accountNumber: form.accountNumber.value,
        accountHolderName: form.accountHolderName.value,
      };
      const last4 = details.accountNumber.replace(/\s+/g, "").slice(-4);
      payment = { bankAccountId: null, label: accountLabel(details.bankName, last4), isNew: true, details };
    }

    setBusy(accountNext, true, "Đang gửi mã OTP...");
    try {
      await sendOtp();
      openOtpStep();
    } catch (error) {
      if (!handleHoldError(error)) showError(error.message);
    } finally {
      setBusy(accountNext, false, "Tiếp tục");
    }
  });

  accountList.addEventListener("change", clearMessages);

  document.getElementById("show-new-account").addEventListener("click", () => {
    clearMessages();
    addingAccount = true;
    showAccountChoice();
    document.getElementById("account-number").focus();
  });

  useSavedButton.addEventListener("click", () => {
    clearMessages();
    addingAccount = false;
    showAccountChoice();
  });

  // ---- Step 2: OTP ----

  steps.otp.addEventListener("submit", (event) => {
    event.preventDefault();
    clearMessages();
    if (!otpInput.reportValidity()) return;
    reviewAccount.textContent = payment.label;
    goTo("confirm");
    confirmButton.focus();
  });

  document.getElementById("otp-back").addEventListener("click", () => {
    clearMessages();
    goTo("account");
  });

  document.getElementById("otp-resend").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await sendOtp();
      otpInput.value = "";
      showNotice("Đã gửi mã OTP mới.");
      otpInput.focus();
    } catch (error) {
      if (!handleHoldError(error)) showError(error.message);
    } finally {
      button.disabled = expired;
    }
  });

  // ---- Step 3: confirm ----

  document.getElementById("confirm-back").addEventListener("click", () => {
    clearMessages();
    goTo("otp");
    otpInput.focus();
  });

  steps.confirm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();
    setBusy(confirmButton, true, "Đang thanh toán...");
    try {
      await apiRequest("POST", `/api/bookings/${bookingId}/payment`, {
        bankAccountId: payment.bankAccountId,
        paymentMethod: "BANK_TRANSFER",
        otp: otpInput.value,
      });
      paid = true;
      window.location.assign(root.dataset.successUrl);
    } catch (error) {
      if (handleHoldError(error)) return;
      if (error.code === "INVALID_OTP" || error.code === "VERIFICATION_EXPIRED_OR_LOCKED") {
        // Wrong, expired or locked OTP: type it again or ask for a new one.
        openOtpStep();
      } else if (error.code === "PAYMENT_FAILED") {
        // The bank declined and the OTP is used up. A new account is saved by
        // now, so it appears in the saved list; start again from step 1.
        goTo("account");
        await loadAccounts(payment.bankAccountId);
      }
      showError(error.message);
    } finally {
      // After a successful payment the button stays disabled while the page leaves.
      if (!paid) setBusy(confirmButton, false, "Xác nhận thanh toán");
    }
  });

  goTo("account");
  tick();
  loadAccounts();
})();
