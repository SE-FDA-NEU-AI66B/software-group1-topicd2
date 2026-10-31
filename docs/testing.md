# Milestone 4 - Testing Document

**Team:** Team 01 - SmashGo

**Topic:** D2 - Sports Platform

**Members:**

- Chử Vũ Thảo Hiền (ID: 11247287)
- Phan Thị Anh Quỳnh (ID: 11247347)
- Bùi Phương Thảo (ID: 11247353)

**Product Owner:** @dqchien

**Scrum Master (Sprint 4):** TODO

**Repository:** https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2

**Project board:** https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24

**Setup guide:** https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2/blob/main/docs/SETUP.md

**Submitted by:** Chử Vũ Thảo Hiền

---

## 1. What we test, and why

| Layer | Test | Why |
| --- | --- | --- |
| services | TODO | TODO |
| repository (db) | TODO | TODO |
| routes | TODO | TODO |
| interface (UI) | TODO | TODO |

TODO: 2-3 sentences on risk (which parts are tested most, and why).

## 2. Test cases for every P0 story

Kind values: normal, error, boundary (just below), boundary (on the limit), boundary (just above).

### US-01 - View Available Badminton Courts

Reserved IDs: TC-01 to TC-04. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: none. Codes: 400 INVALID_COURT_FILTER

### US-02 - View Detailed Court Information

Reserved IDs: TC-05 to TC-07. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: none. Codes: 404 COURT_NOT_FOUND

### US-03 - View Available Time Slots

Reserved IDs: TC-08 to TC-11. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: BR2. Codes: 400 INVALID_AVAILABILITY_DATE; 404 COURT_NOT_FOUND

### US-04 - Book One Available Time Slot

Reserved IDs: TC-12 to TC-22. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: BR1, BR2, BR3, BR6, BR7. Codes: 400 INVALID_INPUT, INVALID_OTP; 401 UNAUTHENTICATED; 403 NOT_BOOKING_OWNER, NOT_ACCOUNT_OWNER; 404 COURT_NOT_FOUND, BOOKING_NOT_FOUND, BANK_ACCOUNT_NOT_FOUND; 409 SLOT_UNAVAILABLE, ACTIVE_BOOKING_LIMIT, HOLD_EXPIRED_OR_ALREADY_PAID, VERIFICATION_EXPIRED_OR_LOCKED, BANK_ACCOUNT_EXISTS; 422 BOOKING_RULE_VIOLATION, BANK_ACCOUNT_NOT_VERIFIED; 502 PAYMENT_FAILED

### US-05 - Prevent Double Booking

Reserved IDs: TC-23 to TC-26. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: BR1. Codes: 409 SLOT_UNAVAILABLE

### US-11 - Activate or Deactivate Badminton Courts

Reserved IDs: TC-27 to TC-31. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: none. Codes: 400 INVALID_STATUS; 401 UNAUTHENTICATED; 403 ADMIN_REQUIRED; 404 COURT_NOT_FOUND; 409 COURT_HAS_UPCOMING_BOOKINGS

### US-12 - Approve or Reject Court Request

Reserved IDs: TC-32 to TC-36. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-?? | | | | |

Rules: none. Codes: 400 INVALID_STATUS_FILTER, INVALID_DECISION; 401 UNAUTHENTICATED; 403 ADMIN_REQUIRED; 404 REQUEST_NOT_FOUND; 409 REQUEST_ALREADY_REVIEWED

## 3. Automated tests

Command: `python -m pytest -v`

- **No server, no real database:** tests call the Flask app through its test client. The `database_path` fixture in `tests/conftest.py` builds a fresh SQLite file in pytest's `tmp_path` from `schema.sql` for every test and seeds a minimal data set (2 Users, 1 Manager, 1 Admin, 2 ACTIVE courts with opening hours, 1 verified bank account). Nothing reads `instance/`, `.env` or a database dump; only `tests/test_app.py` runs `init_db.py`, because it tests the demo seed itself.
- **Fixed clock:** application code reads the time through `clock.now()` / `clock.today()`. The autouse `frozen_clock` fixture pins it to Monday 2030-01-07 09:00, and tests move it with `frozen_clock.advance(...)` (for example to expire the 10-minute hold, BR3), so results never depend on the day the suite runs.
- **Fake bank gateway:** the autouse `fake_gateway` fixture replaces `bank_gateway.send_otp` and `charge`: the OTP is always `123456`, no outside service is called, every OTP and charge is recorded, and `fake_gateway.fail_charges = True` simulates `PAYMENT_FAILED`.
- **Test case IDs:** a test that implements a case in section 2 carries the ID in a comment directly above it, for example `# TC-08: ...`, so `grep TC-08 tests/` finds it.
- **Where:** all tests live in `tests/`; shared constants and helpers are in `tests/support.py`. Run `pytest` (or `python -m pytest -v`) from the repository root; `pytest.ini` sets `testpaths = tests`. Test dependencies: `pip install -r requirements-dev.txt`.

[SCREENSHOT: full output of python -m pytest -v, every test name visible]

## 4. What the tests found

- Bug or rule broken on purpose: TODO
- Red test output (if no bug was found): TODO
- Fix: TODO
- Guarding test: TODO (TC-xx)