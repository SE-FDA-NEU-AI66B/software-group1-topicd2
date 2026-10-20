# UI Screens and Flows

This document maps user stories to the screens and routes currently implemented
in the application. P0 screens have a wireframe in `docs/images/ui/`.

## Story, screen, route, and status

| Story | Screen | Purpose | Route | Priority | API endpoints used | Status |
|-------|--------|---------|-------|----------|--------------------|--------|
| US-01 | Court list and filters | The user comes here to find courts by location and requested date/time. | `GET /courts` (`/` redirects here) | P0 | `GET /api/courts` | Implemented |
| US-02, US-03 | Court details and availability | The user comes here to review a court and choose an available time slot. | `GET /courts/{courtId}` | P0 | `GET /api/courts/{courtId}`, `GET /api/courts/{courtId}/availability?date=...` | Implemented |
| US-04, US-05 | Select court, date, and time; create a booking hold | The user comes here to confirm a slot and hold it for payment. | `GET /book` | P0 | `POST /api/bookings` | Implemented |
| US-04 | Payment, bank account, and OTP verification | The user comes here to verify a payment account and pay for a held booking. | `GET /book?bookingId={bookingId}` | P0 | `GET /api/bank-accounts`, `POST /api/bank-accounts`, `POST /api/bank-accounts/{bankAccountId}/verify`, `POST /api/bookings/{bookingId}/payment` | Implemented |
| US-04 | Sign in and return to the requested screen | The user comes here to sign in and resume the action they started. | `GET/POST /login` | P0 | Form submission to `POST /login` | Implemented |
| US-04 | Create a User account and continue booking | The user comes here to register before continuing to the requested screen. | `GET/POST /register` | P0 | Form submission to `POST /register` | Implemented |
| US-04; US-06 and US-08 actions are P1 | View booking status and manage bookings | The user comes here to view the status and details of their bookings. | `GET /my-bookings` | P0 (view); P1 (cancel/history) | `GET /api/bookings/mine`; `DELETE /api/bookings/{bookingId}` (P1 cancel) | Implemented |
| US-11, US-12 | Review court requests and manage court status | The user comes here to review new court requests and control court availability as an Admin. | `GET /admin/courts` | P0 | `GET /api/admin/court-requests`, `POST /api/admin/court-requests/{requestId}/review`, `GET /api/admin/courts`, `PATCH /api/admin/courts/{courtId}/status` | Implemented |
| US-15, US-16, US-17 | Manager court workspace | The Manager would come here to manage owned courts and track submissions. | `GET /manager/courts` | P1 | None; the route currently renders an unsupported-feature placeholder | Placeholder |

### P0 wireframes

| Screen(s) | Wireframe |
|-----------|-----------|
| Court list, details, and availability | [images/ui/courts-availability.svg](images/ui/courts-availability.svg) |
| Booking and hold creation | [images/ui/book.svg](images/ui/book.svg) |
| Login and registration | [images/ui/auth.svg](images/ui/auth.svg) |
| Payment, bank account, and OTP | [images/ui/payment.svg](images/ui/payment.svg) |
| My bookings | [images/ui/my-bookings.svg](images/ui/my-bookings.svg) |
| Admin court review and status management | [images/ui/admin-courts.svg](images/ui/admin-courts.svg) |

## Screen flow

### Guest and User booking flow

```text
GET / or /courts
  -> filter courts by location/date/time
  -> GET /courts/{courtId}
       -> GET /api/courts/{courtId}
       -> GET /api/courts/{courtId}/availability?date=...
  -> choose an available slot
  -> GET /book?courtId=...&date=...&startTime=...&endTime=...
       -> if Guest: GET/POST /login or GET/POST /register, then return to /book
  -> POST /api/bookings
       -> create a 10-minute PENDING hold
  -> GET /book?bookingId={bookingId}
       -> link bank account if needed, then verify with OTP
       -> POST /api/bookings/{bookingId}/payment
  -> GET /my-bookings
```

An authenticated User skips sign-in and registration. `/` is a redirect to
`/courts`, not a separate screen. The M1 `/availability` screen is replaced by
the filters on `/courts` and date-specific availability on
`/courts/{courtId}`; `/availability` is not a current application route.

### Admin flow

```text
GET/POST /login
  -> role = ADMIN
  -> GET /admin/courts
       -> GET /api/admin/court-requests
       -> POST /api/admin/court-requests/{requestId}/review
       -> GET /api/admin/courts
       -> PATCH /api/admin/courts/{courtId}/status
```

### Manager flow

```text
GET/POST /login
  -> role = MANAGER
  -> GET /manager/courts
       -> P1 route; the page is currently an unsupported-feature placeholder
```

## Error messages

API errors use the response shape `{ "code": "...", "message": "..." }`. The
screen presenting an actionable error should preserve the form values and show
the message as an alert. These M2 messages are the required user-facing copy:

| HTTP status | Code | Rule | Message |
|--------------|------|------|---------|
| 409 | `SLOT_UNAVAILABLE` | BR1 | “This court was just booked for that time. Please choose another time or court.” |
| 409 | `ACTIVE_BOOKING_LIMIT` | BR6 | “You already have 2 active bookings. Complete or cancel one before booking another.” |
| 422 | `BOOKING_RULE_VIOLATION` | BR2 | “A booking must last at least 1 hour. Choose a later end time.” |
| 422 | `BANK_ACCOUNT_NOT_VERIFIED` | BR7 | “Your bank account is not verified yet. Enter the OTP to verify it before paying.” |
| 409 | `HOLD_EXPIRED_OR_ALREADY_PAID` | BR3 | “The 10-minute hold has ended and the slot was released. Please book again.” |

`SLOT_UNAVAILABLE`, `ACTIVE_BOOKING_LIMIT`, and `BOOKING_RULE_VIOLATION` are
returned by `POST /api/bookings`. `BANK_ACCOUNT_NOT_VERIFIED` and
`HOLD_EXPIRED_OR_ALREADY_PAID` are returned by
`POST /api/bookings/{bookingId}/payment`.
