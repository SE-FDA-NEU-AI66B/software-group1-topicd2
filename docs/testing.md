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
| TC-01 | US-01 | `GET /api/courts?date=<tomorrow>&startTime=20:00&endTime=21:00`; court A booked 20:00-22:00, one DISABLED and one MAINTENANCE court | 200, only court B listed; booked, DISABLED and MAINTENANCE courts left out | normal |
| TC-02 | US-01 | Filter missing `date`, `startTime` or `endTime`; time not on a 30-minute step (19:15, 20:10); invalid date | 400 `INVALID_COURT_FILTER` | error |
| TC-03 | US-01 | Filter window 19:00-20:00 (60 minutes) | 200, both free courts listed | boundary (on the limit) |
| TC-04 | US-01 | Filter window 19:00-19:30 (30 minutes) | 400 `INVALID_COURT_FILTER` | boundary (just below) |

Rules: none. Codes: 400 INVALID_COURT_FILTER

### US-02 - View Detailed Court Information

Reserved IDs: TC-05 to TC-07. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-05 | US-02 | `GET /api/courts/1` (ACTIVE court with two images stored out of order) | 200 with price 100000, address, description, opening hours, images ordered by `sortOrder` (0, 1) | normal |
| TC-06 | US-02 | `GET /api/courts/9999` | 404 `COURT_NOT_FOUND` | error |
| TC-07 | US-02 | `GET /api/courts/1` after court 1 is set to DISABLED or MAINTENANCE | 404 `COURT_NOT_FOUND` | error |

Rules: none. Codes: 404 COURT_NOT_FOUND

### US-03 - View Available Time Slots

Reserved IDs: TC-08 to TC-11. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-08 | US-03 | `GET /api/courts/1/availability?date=<tomorrow>` (open 06:00-22:00, no bookings) | 200; first slot 06:00; every slot lasts 60 minutes; slots start 30 minutes apart; all `AVAILABLE` | normal |
| TC-09 | US-03 | Same request with a booking 20:00-22:00 and a `Court_Block` 10:00-12:00 | Slots overlapping them (09:30-11:30, 19:30-21:00) are `BOOKED`, `available: false`; 12:00 and 19:00 stay `AVAILABLE`; 18:30 is `UNAVAILABLE` (BR2 short gap) | normal |
| TC-10 | US-03 | `date` missing, empty, `not-a-date` or `2030-02-30` | 400 `INVALID_AVAILABILITY_DATE` | error |
| TC-11 | US-03 | Court A closes 22:00, court B closes 21:00 | Last slot ends exactly at CloseTime (21:00-22:00, 20:00-21:00) is offered; a slot starting 30 minutes later (21:30, 20:30) is not | boundary (on the limit / just above) |

Rules: BR2. Codes: 400 INVALID_AVAILABILITY_DATE; 404 COURT_NOT_FOUND

### US-04 - Book One Available Time Slot

Reserved IDs: TC-12 to TC-22. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-12 | US-04 | `POST /api/bookings` for an available court and slot | 201, status `PENDING`, `HoldExpiresAt` is 10 minutes after the fixed clock | normal |
| TC-13 | US-04 | Start 08:00, end 08:59 (59 minutes) | 422 `BOOKING_RULE_VIOLATION` | boundary (just below) |
| TC-14 | US-04 | Start 08:00, end 09:00 (60 minutes) | 201 | boundary (on the limit) |
| TC-15 | US-04 | Start 08:00, end 09:01 (61 minutes) | 201 | boundary (just above) |
| TC-16 | US-04 | Existing booking 20:00-21:00; request 19:00-20:00 (0-minute gap) | 201 | boundary (on the limit) |
| TC-17 | US-04 | Existing booking 20:00-21:00; request 18:30-19:30 (30-minute gap) | 422 `BOOKING_RULE_VIOLATION` | boundary (just below) |
| TC-18 | US-04 | Existing booking 20:00-21:00; request 18:00-19:00 (60-minute gap) | 201 | boundary (on the limit) |
| TC-19 | US-04 | Request an occupied slot held by unexpired `PENDING`, `EXPIRED`, or `CANCELLED` booking | Pending hold: 409 `SLOT_UNAVAILABLE`; expired/cancelled: 201 | normal / error |
| TC-20 | US-04 | User's first and second active bookings | Both return 201 | normal |
| TC-21 | US-04 | User already has 2 active bookings, then tries a third; mark previous bookings `CANCELLED` and `EXPIRED` and retry | Third active booking: 409 `ACTIVE_BOOKING_LIMIT`; inactive bookings do not count and retry returns 201 | error / normal |
| TC-22 | US-04 | Guest request; missing fields; malformed date/time/court ID; start off 30-minute step; unknown court; non-player role | 401 `UNAUTHENTICATED`; 400 `INVALID_INPUT`; 404 `COURT_NOT_FOUND`; 403 `FORBIDDEN` | error |

Rules: BR1, BR2, BR3, BR6, BR7. Codes: 400 INVALID_INPUT, INVALID_OTP; 401 UNAUTHENTICATED; 403 NOT_BOOKING_OWNER, NOT_ACCOUNT_OWNER; 404 COURT_NOT_FOUND, BOOKING_NOT_FOUND, BANK_ACCOUNT_NOT_FOUND; 409 SLOT_UNAVAILABLE, ACTIVE_BOOKING_LIMIT, HOLD_EXPIRED_OR_ALREADY_PAID, VERIFICATION_EXPIRED_OR_LOCKED, BANK_ACCOUNT_EXISTS; 422 BOOKING_RULE_VIOLATION, BANK_ACCOUNT_NOT_VERIFIED; 502 PAYMENT_FAILED

### US-05 - Prevent Double Booking

Reserved IDs: TC-23 to TC-26. Needs at least 3 cases: 1 normal, 1 error; if the rule has a number, boundary cases on both sides.

| ID | Story | Input | Expected | Kind |
| --- | --- | --- | --- | --- |
| TC-23 | US-05 | Existing booking 20:00-22:00; request 19:30-20:30 (partial overlap) | 409 `SLOT_UNAVAILABLE` | error |
| TC-24 | US-05 | Existing booking 20:00-22:00; request 19:00-20:00 (adjacent, no overlap) | 201 | normal |
| TC-25 | US-05 | Two concurrent requests from separate connections for the same court and slot, using `BEGIN IMMEDIATE` | Exactly one succeeds; the other returns `409 SLOT_UNAVAILABLE` | normal / error |
| TC-26 | US-05 | Repository insert with `EndTime <= StartTime` | SQLite `CHECK` constraint raises `IntegrityError` | error |

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