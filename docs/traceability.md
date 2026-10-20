# Traceability

Every screen traces back to a feature and forward to the issue that built it.
This table is the single source of truth for Milestone 1 section 6 and for the
Milestone 4 report. Keep it current - a PR that adds a route and does not
update this file should not be approved.

| Route | Purpose | Access | Priority | Feature | Story issue | PR | Status |
|-------|---------|--------|----------|---------|-------------|-----|--------|
| `/` | Landing page | G | P0 | F1 | #3 | #14 | Done |
| `/courts` | List active courts with location and date/time filters; links to details and prefilled booking (`GET /api/courts`) | G, U | P0 | F1 | US-01 (#95) | — | In progress |
| `/courts/{courtId}` | Show active court price, photos, address and condition; load date-based availability (`GET /api/courts/{id}`, `GET /api/courts/{id}/availability`) | G, U | P0 | F1 | US-02, US-03 (#95) | — | In progress |
| `/book` | Select court, date and time, then hold the slot (`POST /api/bookings`) | G, U | P0 | F2 | US-04, US-05 (#91) | — | In progress |
| `/book?bookingId=` | Payment step: 10-minute countdown, link bank account, OTP, pay (`/api/bank-accounts`, `POST /api/bookings/{id}/payment`) | U | P0 | F2 | US-04 (#92) | — | In progress |
| `/my-bookings` | List own bookings with status (loading, empty, error, data); pay a pending one; cancel with BR4 refund (`GET /api/bookings/mine`, `DELETE /api/bookings/{id}`) | U | P0 (view); P1 (cancel) | F3 | US-06, US-08 (#93) | — | In progress |
| `/admin/courts` | Review court requests and activate/deactivate courts (`GET /api/admin/court-requests`, `POST /api/admin/court-requests/{id}/review`, `GET /api/admin/courts`, `PATCH /api/admin/courts/{id}/status`) | A | P0 | F4 | US-11 (#94) | — | In progress |

**Access codes:** G = guest (not logged in) · U = authenticated user · A = admin

**Status:** Not started / In progress / Done

## Business rules

Numbered, so issues and tests can cite them.

| # | Rule | Enforced where | Tested by |
|---|------|----------------|-----------|
| BR1 | A court cannot be double-booked for a slot that is already reserved. | `booking_service.create_booking` (overlap check inside `BEGIN IMMEDIATE`) | `tests/test_booking.py`: `test_overlapping_seeded_booking_is_rejected_with_clear_message`, `test_simultaneous_requests_for_same_slot_have_one_winner` |
| BR2 | A booking lasts at least 1 hour; back-to-back bookings must be contiguous. | `booking_service._check_booking_rules`, `_check_slot` | `tests/test_booking.py`: `test_booking_rule_violations`, `test_contiguous_booking_is_allowed` |
| BR3 | A slot is held for 10 minutes pending payment. | `booking_service.create_booking` (`HoldExpiresAt`), `_release_expired_holds`; `payment_service.pay_booking` rejects expired holds | `tests/test_booking.py`: `test_create_booking_holds_slot_for_ten_minutes`, `test_expired_hold_releases_slot`; `tests/test_payment.py`: `test_expired_hold_cannot_be_paid` |
| BR4 | Cancelling more than 4 hours before play refunds in full; within 4 hours 50% of the deposit is kept. | `booking_service.cancel_booking`, `refund_for` | `tests/test_my_bookings.py`: `test_cancel_more_than_four_hours_before_refunds_in_full`, `test_cancel_within_four_hours_keeps_half_the_deposit`, `test_exactly_four_hours_before_is_late_cancellation` |
| BR5 | A reminder is scheduled 4 hours before play time. | `payment_service.pay_booking` (inserts `BOOKING_REMINDER` notification) | `tests/test_payment.py`: `test_payment_confirms_booking_and_schedules_reminder` |
| BR6 | At most 2 active (upcoming) bookings per account. | `booking_service._check_active_limit` | `tests/test_booking.py`: `test_third_active_booking_is_rejected` |
| BR7 | Payment requires a bank account linked and verified by OTP. | `payment_service.link_bank_account`, `verify_bank_account`, `pay_booking` | `tests/test_payment.py`: `test_unverified_account_cannot_pay`, `test_wrong_otp_three_times_locks_verification`, `test_expired_otp_is_rejected` |
