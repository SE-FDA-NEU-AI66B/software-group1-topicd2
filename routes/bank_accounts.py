from flask import Blueprint, current_app, jsonify, request

from booking_service import BookingError
from payment_service import link_bank_account, list_bank_accounts, verify_bank_account
from routes.bookings import api_user, error_response

bank_accounts_bp = Blueprint("bank_accounts", __name__, url_prefix="/api/bank-accounts")


@bank_accounts_bp.get("")
def api_list_bank_accounts():
    current_user, error = api_user()
    if error:
        return error
    return jsonify(list_bank_accounts(current_app.config["DATABASE_PATH"], current_user["user_id"]))


@bank_accounts_bp.post("")
def api_link_bank_account():
    current_user, error = api_user()
    if error:
        return error

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}

    try:
        account = link_bank_account(
            current_app.config["DATABASE_PATH"],
            current_user["user_id"],
            payload.get("bankName"),
            payload.get("accountNumber"),
            payload.get("accountHolderName"),
        )
    except BookingError as booking_error:
        return error_response(booking_error)
    return jsonify(account), 201


@bank_accounts_bp.post("/<int:bank_account_id>/verify")
def api_verify_bank_account(bank_account_id: int):
    current_user, error = api_user()
    if error:
        return error

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}

    try:
        result = verify_bank_account(
            current_app.config["DATABASE_PATH"],
            current_user["user_id"],
            bank_account_id,
            payload.get("otp"),
        )
    except BookingError as booking_error:
        return error_response(booking_error)
    return jsonify(result), 200
