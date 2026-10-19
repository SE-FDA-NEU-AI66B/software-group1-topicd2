"""Mock bank gateway used for local development and demos.

The real gateway is out of scope for the course project. This mock behaves
deterministically so the payment flow can be demonstrated and tested:

- every OTP it "sends" is MOCK_OTP;
- a charge fails when the account number ends with FAILING_ACCOUNT_SUFFIX,
  so PAYMENT_FAILED can be demonstrated.

See docs/SETUP.md for the values.
"""

import secrets

MOCK_OTP = "123456"
FAILING_ACCOUNT_SUFFIX = "0000"
SUPPORTED_BANKS = (
    "Vietcombank",
    "VietinBank",
    "BIDV",
    "Agribank",
    "Techcombank",
    "MB Bank",
    "ACB",
    "TPBank",
)


def send_otp(bank_name: str, account_number: str) -> str:
    """Pretend to send an OTP to the account holder and return it."""
    return MOCK_OTP


def charge(bank_name: str, account_number: str, amount: float) -> str | None:
    """Charge the account. Returns a transaction code, or None on failure."""
    if account_number.endswith(FAILING_ACCOUNT_SUFFIX):
        return None
    return f"MOCK-{secrets.token_hex(6).upper()}"
