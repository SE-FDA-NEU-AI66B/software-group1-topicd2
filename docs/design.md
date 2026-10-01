# Milestone 2 - Design Document

**Team:** Team 01 - SmashGo

**Topic:** D2 - Sports Platform

**Members:**

- Chử Vũ Thảo Hiền
- Phan Thị Anh Quỳnh
- Bùi Phương Thảo

**Product Owner:** @dqchien

**Scrum Master:** @Buithaoaineu (Sprint 2)

**Repository:** https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git

**Project board:** https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24

**Setup guide:** N/A

**Submitted by:** Chử Vũ Thảo Hiền

---

<img src="..\images\sprint2-planning1.PNG" alt="Sprint 2 Planning.1" width="500">
<img src="..\images\Sprint2-planning.PNG" alt="Sprint 2 Planning.2" width="500">

---

## 1. Architecture

SmashGo is a badminton court booking platform with four user roles: **Guest** (browses courts), **User** (books and pays), **Manager** (court owner: adds, edits and deletes their own courts) and **Admin** (approves new courts, tracks commission). All four roles use the system through a web browser. The diagram below shows the container level (C4): what runs where, and what travels along every arrow.

![SmashGo architecture diagram](..\images\architecture.png)

### 1.1 Components

| Component              | Runs where                                             | Responsibility                                                                                                                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Browser                | User's phone or computer                               | Shows pages to Guest, User, Manager and Admin; sends forms, search filters and booking requests.                                                                                                                                                                 |
| SmashGo Web App        | Application server (`<framework>`)                     | Handles routes, login, role checks (Guest / User / Manager / Admin) and renders pages, including the in-app notifications shown to the user. Passes validated requests to the Booking Service.                                                                   |
| Booking Service        | Same server, separate module (`src/<booking_service>`) | Enforces the business rules: no double booking of one court in one time slot, new-court requests waiting for Admin approval, commission, court recommendation by filter, booking reminders (created as in-app notifications), and usage statistics by time slot. |
| Database               | Database file or server (`<database>`)                 | Stores users, courts, bookings, court requests, court reports and notifications. Its constraints back up the rules above.                                                                                                                                        |
| Bank / Payment gateway | External system                                        | Links the User's bank and confirms payment for a booking.                                                                                                                                                                                                        |

### 1.2 Connections

| From → To                                | What travels along it                                                                                                 |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Browser → Web App                        | HTTP request (login form, search filters, booking form, court management form)                                        |
| Web App → Browser                        | Rendered pages (HTML), including in-app notifications                                                                 |
| Web App → Booking Service                | Function call (validated request together with the user's role)                                                       |
| Booking Service → Database               | SQL query (SELECT free time slots, INSERT booking, INSERT court request, UPDATE approval status, INSERT notification) |
| Booking Service → Bank / Payment gateway | HTTPS API call (payment request, bank link)                                                                           |
| Bank / Payment gateway → Booking Service | HTTPS callback (payment result)                                                                                       |

### 1.3 How the main flows move through the system

- **User books a court:** Browser sends the booking form (HTTP request) → Web App checks that the user is logged in → Booking Service checks the time slot is free and inserts the booking (SQL query; the database rejects a second booking of the same court and slot) → Booking Service asks the Bank for payment (HTTPS API call) → page confirms the booking.
- **Manager adds a new court:** Manager submits the court form → Booking Service stores it as a request with status "pending" (SQL query) → Admin sees the pending request on their page and approves or rejects it → only approved courts appear to Guests and Users.
- **Reminder:** the Booking Service checks for bookings starting in about 4 hours (SQL query) and saves a reminder notification for each User (SQL query). The next time the User's browser loads a page (HTTP request), the Web App reads the unread notifications and shows them in the page. Notifications are sent from inside the app; no external notification service is used.

---

## 2. Data model

### 2.1 ERD

![ERD](..\images\erd.png)

### 2.2 Table descriptions

#### `Users`: Stores all user accounts and their roles in the SmashGo system.

| Column       | Type         | PK  | FK  | Constraint                                                 | Enforces (M1 rule)     |
| ------------ | ------------ | --- | --- | ---------------------------------------------------------- | ---------------------- |
| UserID       | INTEGER      | ✔   |     | `PRIMARY KEY`, `AUTO_INCREMENT`                            |                        |
| FullName     | VARCHAR(100) |     |     | `NOT NULL`                                                 |                        |
| Email        | VARCHAR(150) |     |     | `NOT NULL`, `UNIQUE`                                       |                        |
| PasswordHash | VARCHAR(255) |     |     | `NOT NULL`                                                 |                        |
| Phone        | VARCHAR(20)  |     |     |                                                            |                        |
| Role         | VARCHAR(20)  |     |     | `NOT NULL`, `CHECK (Role IN ('USER', 'MANAGER', 'ADMIN'))` | Access rules, BR6, BR7 |
| CreatedAt    | DATETIME     |     |     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                    |                        |

`Role` determines whether an account acts as a User, Manager, or Admin. Self-registration creates only accounts with role `USER`; Manager and Admin accounts are provisioned separately. Access to protected functions is controlled according to the user's role. The table is named `Users` (not `User`) because `USER` is a reserved keyword in most SQL databases. Only a password hash is stored, never the plain password.

---

#### `Court`: Stores badminton court information, ownership, operating hours, availability status, and hourly price.

| Column       | Type          | PK  | FK             | Constraint                                                            | Enforces (M1 rule)        |
| ------------ | ------------- | --- | -------------- | --------------------------------------------------------------------- | ------------------------- |
| CourtID      | INTEGER       | ✔   |                | `PRIMARY KEY`, `AUTO_INCREMENT`                                       |                           |
| ManagerID    | INTEGER       |     | `Users.UserID` | `NOT NULL`                                                            | Manager ownership rule    |
| CourtName    | VARCHAR(100)  |     |                | `NOT NULL`                                                            | US-10                     |
| Location     | VARCHAR(255)  |     |                | `NOT NULL`                                                            | US-02, US-10              |
| Description  | TEXT          |     |                |                                                                       | US-02                     |
| PricePerHour | DECIMAL(10,2) |     |                | `NOT NULL`, `CHECK (PricePerHour >= 0)`                               | US-02, US-10              |
| OpenTime     | TIME          |     |                | `NOT NULL`                                                            | US-03                     |
| CloseTime    | TIME          |     |                | `NOT NULL`, `CHECK (CloseTime > OpenTime)`                            | US-03                     |
| Status       | VARCHAR(20)   |     |                | `NOT NULL`, `CHECK (Status IN ('ACTIVE', 'DISABLED', 'MAINTENANCE'))` | US-01, Court disable rule |
| CreatedAt    | DATETIME      |     |                | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                               |                           |

`ManagerID` identifies the Manager who owns the court. A Manager can only view and edit their own courts, and can only add a new court by submitting a `Court_Request` that an Admin approves. Admin can manage courts across all Managers. A court with upcoming bookings cannot be disabled. `OpenTime` and `CloseTime` define the hours in which time slots can be offered to Users. Only courts with status `ACTIVE` appear in search results and can be booked.

---

#### `Court_Image`: Stores the photos of a court shown on the court detail page.

| Column    | Type         | PK  | FK              | Constraint                              | Enforces (M1 rule) |
| --------- | ------------ | --- | --------------- | --------------------------------------- | ------------------ |
| ImageID   | INTEGER      | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`         |                    |
| CourtID   | INTEGER      |     | `Court.CourtID` | `NOT NULL`, `ON DELETE CASCADE`         | US-02              |
| Url       | VARCHAR(500) |     |                 | `NOT NULL`                              | US-02              |
| SortOrder | INTEGER      |     |                 | `NOT NULL`, `DEFAULT 0`                 | US-02              |
| CreatedAt | DATETIME     |     |                 | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` |                    |

A court can have many photos. `SortOrder` decides the display order; the photo with the lowest value is shown first.

---

#### `Court_Block`: Stores time ranges in which a court cannot be booked (maintenance, events).

| Column    | Type         | PK  | FK              | Constraint                                | Enforces (M1 rule)     |
| --------- | ------------ | --- | --------------- | ----------------------------------------- | ---------------------- |
| BlockID   | INTEGER      | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`           |                        |
| CourtID   | INTEGER      |     | `Court.CourtID` | `NOT NULL`, `ON DELETE CASCADE`           | US-03                  |
| BlockDate | DATE         |     |                 | `NOT NULL`                                | US-03                  |
| StartTime | TIME         |     |                 | `NOT NULL`                                | US-03                  |
| EndTime   | TIME         |     |                 | `NOT NULL`, `CHECK (EndTime > StartTime)` | US-03                  |
| Reason    | VARCHAR(255) |     |                 |                                           |                        |
| CreatedBy | INTEGER      |     | `Users.UserID`  | `NOT NULL`                                | Manager ownership rule |
| CreatedAt | DATETIME     |     |                 | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`   |                        |

Time slots that fall inside a block are shown as unavailable when Users view the court schedule. `CreatedBy` must be the court's Manager or an Admin.

---

#### `Booking`: Records a user's reservation for a specific court, date, and time interval.

| Column                | Type          | PK  | FK              | Constraint                                                                                                  | Enforces (M1 rule) |
| --------------------- | ------------- | --- | --------------- | ----------------------------------------------------------------------------------------------------------- | ------------------ |
| BookingID             | INTEGER       | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`                                                                             |                    |
| UserID                | INTEGER       |     | `Users.UserID`  | `NOT NULL`                                                                                                  | BR6, US-08         |
| CourtID               | INTEGER       |     | `Court.CourtID` | `NOT NULL`                                                                                                  | BR1, BR2           |
| BookingDate           | DATE          |     |                 | `NOT NULL`                                                                                                  | BR1, BR2, BR3      |
| StartTime             | TIME          |     |                 | `NOT NULL`                                                                                                  | BR1, BR2, BR3, BR5 |
| EndTime               | TIME          |     |                 | `NOT NULL`, `CHECK (EndTime > StartTime)`                                                                   | BR1, BR2           |
| TotalAmount           | DECIMAL(10,2) |     |                 | `NOT NULL`, `CHECK (TotalAmount >= 0)`                                                                      |                    |
| DepositAmount         | DECIMAL(10,2) |     |                 | `NOT NULL`, `CHECK (DepositAmount >= 0)`                                                                    | BR4                |
| Status                | VARCHAR(20)   |     |                 | `NOT NULL`, `CHECK (Status IN ('PENDING', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED', 'EXPIRED'))` | BR1, BR3, BR4, BR6 |
| HoldExpiresAt         | DATETIME      |     |                 |                                                                                                             | BR3                |
| ReminderOffsetMinutes | INTEGER       |     |                 | `NOT NULL`, `DEFAULT 240`, `CHECK (ReminderOffsetMinutes > 0)`                                              | BR5, US-07         |
| CancelledAt           | DATETIME      |     |                 |                                                                                                             | BR4, US-06         |
| CancelledBy           | INTEGER       |     | `Users.UserID`  |                                                                                                             | US-06              |
| CancelReason          | VARCHAR(255)  |     |                 |                                                                                                             | US-06              |
| CreatedAt             | DATETIME      |     |                 | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                                                                     | BR3                |

`Booking` is the central entity connecting a User and a Court. `TotalAmount` is a snapshot of the price at booking time, so later changes to `Court.PricePerHour` do not affect existing bookings. `HoldExpiresAt` records the 10-minute payment-hold deadline; a `PENDING` booking whose deadline has passed is automatically changed to `EXPIRED` and its slot is released. `CancelledAt` is compared with the start time to decide the refund level in BR4 (more than 4 hours before: full refund; within 4 hours: 50% of the deposit is forfeited). `CancelledBy` is the User who owns the booking or the Manager of the court. `ReminderOffsetMinutes` defaults to 240 minutes (4 hours before start) and is used to compute `Notification.ScheduledAt`.

BR1 and BR2 are interval-based business rules and cannot be enforced by a simple `UNIQUE` constraint. A booking in status `PENDING`, `CONFIRMED` or `CHECKED_IN` occupies its time slot, so the overlap check must include `PENDING` bookings that are still being held; `CANCELLED` and `EXPIRED` bookings release the slot. On PostgreSQL this is enforced in the database with an exclusion constraint on `(CourtID, time range of BookingDate + StartTime/EndTime)` filtered by those three statuses. On databases without exclusion constraints, the service performs the check inside a transaction with a row lock (`SELECT ... FOR UPDATE`) or a trigger. The minimum one-hour and contiguous-slot requirements (BR2) and the limit of 2 active bookings per user (BR6) are validated in the Booking Service.

---

#### `Payment`: Records the payment transaction for a booking using a verified bank account.

| Column          | Type          | PK  | FK                          | Constraint                                                                                         | Enforces (M1 rule) |
| --------------- | ------------- | --- | --------------------------- | -------------------------------------------------------------------------------------------------- | ------------------ |
| PaymentID       | INTEGER       | ✔   |                             | `PRIMARY KEY`, `AUTO_INCREMENT`                                                                    |                    |
| BookingID       | INTEGER       |     | `Booking.BookingID`         | `NOT NULL`, `UNIQUE`                                                                               | BR3, BR4           |
| BankAccountID   | INTEGER       |     | `BankAccount.BankAccountID` | `NOT NULL`                                                                                         | BR7                |
| Amount          | DECIMAL(10,2) |     |                             | `NOT NULL`, `CHECK (Amount >= 0)`                                                                  |                    |
| PaymentMethod   | VARCHAR(30)   |     |                             | `NOT NULL`                                                                                         | BR7                |
| TransactionCode | VARCHAR(100)  |     |                             | `UNIQUE`                                                                                           |                    |
| Status          | VARCHAR(20)   |     |                             | `NOT NULL`, `CHECK (Status IN ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED'))` | BR3, BR4, BR7      |
| RefundAmount    | DECIMAL(10,2) |     |                             | `CHECK (RefundAmount >= 0)`                                                                        | BR4                |
| PaidAt          | DATETIME      |     |                             |                                                                                                    | BR3                |
| RefundedAt      | DATETIME      |     |                             |                                                                                                    | BR4                |

Each booking can have at most one payment record in the current model. `Amount` is the amount actually paid for the booking (the deposit in the current model). Payment is allowed only after the user has successfully linked and verified a bank account.

`RefundAmount` and `RefundedAt` support the cancellation/refund policy in BR4: status `REFUNDED` means a full refund, and `PARTIALLY_REFUNDED` means the 50% forfeit case.

---

#### `BankAccount`: Stores bank accounts linked to user accounts for payment.

| Column            | Type         | PK  | FK             | Constraint                              | Enforces (M1 rule) |
| ----------------- | ------------ | --- | -------------- | --------------------------------------- | ------------------ |
| BankAccountID     | INTEGER      | ✔   |                | `PRIMARY KEY`, `AUTO_INCREMENT`         |                    |
| UserID            | INTEGER      |     | `Users.UserID` | `NOT NULL`                              | BR7                |
| BankName          | VARCHAR(100) |     |                | `NOT NULL`                              | BR7                |
| AccountNumber     | VARCHAR(50)  |     |                | `NOT NULL`                              | BR7                |
| AccountHolderName | VARCHAR(150) |     |                | `NOT NULL`                              | BR7                |
| IsVerified        | BOOLEAN      |     |                | `NOT NULL`, `DEFAULT FALSE`             | BR7                |
| VerifiedAt        | DATETIME     |     |                |                                         | BR7                |
| CreatedAt         | DATETIME     |     |                | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` |                    |

Table-level constraint: `UNIQUE (UserID, BankName, AccountNumber)` prevents the same account from being linked twice by one user.

A User can link one or more bank accounts. A bank account must be verified before it can be used for payment. `AccountNumber` is sensitive data and should be encrypted, or only its last 4 digits stored.

---

#### `BankAccountVerification`: Stores OTP verification attempts for linked bank accounts.

| Column         | Type         | PK  | FK                          | Constraint                                                                   | Enforces (M1 rule) |
| -------------- | ------------ | --- | --------------------------- | ---------------------------------------------------------------------------- | ------------------ |
| VerificationID | INTEGER      | ✔   |                             | `PRIMARY KEY`, `AUTO_INCREMENT`                                              |                    |
| BankAccountID  | INTEGER      |     | `BankAccount.BankAccountID` | `NOT NULL`                                                                   | BR7                |
| OTPHash        | VARCHAR(255) |     |                             | `NOT NULL`                                                                   | BR7                |
| ExpiresAt      | DATETIME     |     |                             | `NOT NULL`                                                                   | BR7                |
| AttemptCount   | INTEGER      |     |                             | `NOT NULL`, `DEFAULT 0`, `CHECK (AttemptCount >= 0)`                         | BR7                |
| VerifiedAt     | DATETIME     |     |                             |                                                                              | BR7                |
| Status         | VARCHAR(20)  |     |                             | `NOT NULL`, `CHECK (Status IN ('PENDING', 'VERIFIED', 'FAILED', 'EXPIRED'))` | BR7                |
| CreatedAt      | DATETIME     |     |                             | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                                      | BR7                |

This table records the OTP verification process. `AttemptCount` counts wrong OTP entries; when it reaches the allowed limit the verification is set to `FAILED`. Payment must not proceed unless the corresponding bank account has a successful verification.

---

#### `Notification`: Stores notifications and scheduled booking reminders sent to users.

| Column         | Type         | PK  | FK                  | Constraint                                                                                                                                                            | Enforces (M1 rule) |
| -------------- | ------------ | --- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| NotificationID | INTEGER      | ✔   |                     | `PRIMARY KEY`, `AUTO_INCREMENT`                                                                                                                                       |                    |
| UserID         | INTEGER      |     | `Users.UserID`      | `NOT NULL`                                                                                                                                                            | BR5                |
| BookingID      | INTEGER      |     | `Booking.BookingID` |                                                                                                                                                                       | BR5                |
| Title          | VARCHAR(150) |     |                     | `NOT NULL`                                                                                                                                                            |                    |
| Message        | TEXT         |     |                     | `NOT NULL`                                                                                                                                                            |                    |
| Type           | VARCHAR(30)  |     |                     | `NOT NULL`, e.g. `BOOKING_REMINDER`, `BOOKING_CONFIRMATION`, `CANCELLATION`, `PAYMENT`, `REFUND`, `COURT_REQUEST_RESULT`, `NEW_COURT_REPORT`, `COURT_REPORT_RESPONSE` | BR5                |
| IsRead         | BOOLEAN      |     |                     | `NOT NULL`, `DEFAULT FALSE`                                                                                                                                           |                    |
| ScheduledAt    | DATETIME     |     |                     |                                                                                                                                                                       | BR5                |
| SentAt         | DATETIME     |     |                     |                                                                                                                                                                       | BR5                |
| CreatedAt      | DATETIME     |     |                     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                                                                                                                               |                    |

For a booking reminder, `ScheduledAt` is set to `ReminderOffsetMinutes` (default 4 hours) before the booking's start time. Cancelled bookings must not trigger their scheduled reminder. `BookingID` is empty for notifications that do not belong to a booking, such as the result of a court request or a court report: a Manager is notified when a User reports one of their courts (`NEW_COURT_REPORT`), and the reporting User is notified when the Manager responds (`COURT_REPORT_RESPONSE`).

---

#### `CheckIn`: Records the check-in of a User for a confirmed booking.

| Column      | Type        | PK  | FK                  | Constraint                                     | Enforces (M1 rule) |
| ----------- | ----------- | --- | ------------------- | ---------------------------------------------- | ------------------ |
| CheckInID   | INTEGER     | ✔   |                     | `PRIMARY KEY`, `AUTO_INCREMENT`                |                    |
| BookingID   | INTEGER     |     | `Booking.BookingID` | `NOT NULL`, `UNIQUE`                           | US-09              |
| CheckedInAt | DATETIME    |     |                     | `NOT NULL`                                     | US-09              |
| Status      | VARCHAR(20) |     |                     | `NOT NULL`, `CHECK (Status IN ('CHECKED_IN'))` | US-09              |
| CreatedAt   | DATETIME    |     |                     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`        | US-09              |

A check-in is accepted only when the User has a valid `CONFIRMED` booking for the selected court and time. When accepted, a `CheckIn` row is created and `Booking.Status` is changed to `CHECKED_IN` in the same transaction. An invalid check-in attempt is rejected by the service and does not create any `CheckIn` record. The User and the Court of a check-in are not stored again; they are read through `BookingID`, which avoids inconsistent data.

---

#### `Court_Report`: Records reports submitted by users about badminton courts and their handling by the court's Manager.

| Column          | Type         | PK  | FK              | Constraint                                                                      | Enforces (M1 rule)     |
| --------------- | ------------ | --- | --------------- | ------------------------------------------------------------------------------- | ---------------------- |
| ReportID        | INTEGER      | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`                                                 |                        |
| UserID          | INTEGER      |     | `Users.UserID`  | `NOT NULL`                                                                      |                        |
| CourtID         | INTEGER      |     | `Court.CourtID` | `NOT NULL`                                                                      |                        |
| Reason          | VARCHAR(150) |     |                 | `NOT NULL`                                                                      |                        |
| Description     | TEXT         |     |                 |                                                                                 |                        |
| Status          | VARCHAR(20)  |     |                 | `NOT NULL`, `CHECK (Status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'REJECTED'))` |                        |
| ManagerResponse | TEXT         |     |                 |                                                                                 |                        |
| HandledBy       | INTEGER      |     | `Users.UserID`  |                                                                                 | Manager ownership rule |
| HandledAt       | DATETIME     |     |                 |                                                                                 |                        |
| CreatedAt       | DATETIME     |     |                 | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                                         |                        |

A User can submit reports about a specific Court. The report is sent to the Manager who owns the court (`Court.ManagerID`), and that Manager handles it: they move the status from `OPEN` to `IN_PROGRESS`, then to `RESOLVED` or `REJECTED`, and write their answer in `ManagerResponse`. `HandledBy` must be the same user as `Court.ManagerID` of the reported court; the Booking Service checks this because it cannot be expressed as a simple column constraint. Court reports are an extension beyond the M1 requirements.

---

#### `Court_Request`: Stores court requests (create, update, disable) submitted by Managers and reviewed by Admins.

| Column       | Type          | PK  | FK              | Constraint                                                           | Enforces (M1 rule)     |
| ------------ | ------------- | --- | --------------- | -------------------------------------------------------------------- | ---------------------- |
| RequestID    | INTEGER       | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`                                      |                        |
| ManagerID    | INTEGER       |     | `Users.UserID`  | `NOT NULL`                                                           | Manager ownership rule |
| RequestType  | VARCHAR(20)   |     |                 | `NOT NULL`, `CHECK (RequestType IN ('CREATE', 'UPDATE', 'DISABLE'))` | Admin review rule      |
| CourtID      | INTEGER       |     | `Court.CourtID` |                                                                      | Manager ownership rule |
| CourtName    | VARCHAR(100)  |     |                 |                                                                      |                        |
| Location     | VARCHAR(255)  |     |                 |                                                                      |                        |
| Description  | TEXT          |     |                 |                                                                      |                        |
| PricePerHour | DECIMAL(10,2) |     |                 | `CHECK (PricePerHour >= 0)`                                          |                        |
| OpenTime     | TIME          |     |                 |                                                                      |                        |
| CloseTime    | TIME          |     |                 | `CHECK (CloseTime > OpenTime)`                                       |                        |
| Reason       | TEXT          |     |                 |                                                                      |                        |
| Status       | VARCHAR(20)   |     |                 | `NOT NULL`, `CHECK (Status IN ('PENDING', 'APPROVED', 'REJECTED'))`  | Admin review rule      |
| RejectReason | TEXT          |     |                 |                                                                      | Admin review rule      |
| ReviewedBy   | INTEGER       |     | `Users.UserID`  |                                                                      | Admin review rule      |
| CreatedAt    | DATETIME      |     |                 | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`                              |                        |
| ReviewedAt   | DATETIME      |     |                 |                                                                      |                        |

`ManagerID` identifies the Manager who submits the request. `ReviewedBy` identifies the Admin who reviews it. The referenced `Users` row for `ManagerID` must have role `MANAGER`, while the one for `ReviewedBy` must have role `ADMIN`.

`RequestType` tells what the Manager asks for. For `CREATE`, `CourtID` is empty and `CourtName`, `Location`, `PricePerHour`, `OpenTime` and `CloseTime` are required; when an Admin approves, a new `Court` row is created with this Manager as owner and the images of the request are copied to `Court_Image`. For `UPDATE` and `DISABLE`, `CourtID` is required and must be a court owned by the same Manager; `UPDATE` carries the new values, and `DISABLE` is refused while the court has upcoming bookings. These per-type rules are validated in the Booking Service. When a request is rejected, the Admin explains why in `RejectReason`, and the Manager is notified through a `COURT_REQUEST_RESULT` notification.

---

#### `Court_Request_Image`: Stores the photos attached to a court request.

| Column    | Type         | PK  | FK                        | Constraint                      | Enforces (M1 rule) |
| --------- | ------------ | --- | ------------------------- | ------------------------------- | ------------------ |
| ImageID   | INTEGER      | ✔   |                           | `PRIMARY KEY`, `AUTO_INCREMENT` |                    |
| RequestID | INTEGER      |     | `Court_Request.RequestID` | `NOT NULL`, `ON DELETE CASCADE` | US-02              |
| Url       | VARCHAR(500) |     |                           | `NOT NULL`                      | US-02              |
| SortOrder | INTEGER      |     |                           | `NOT NULL`, `DEFAULT 0`         | US-02              |

The Admin reviews these photos together with the request. They are kept as part of the request history and are copied to `Court_Image` when a `CREATE` request is approved.

---

## 3. API design

The API uses JSON. A successful login sets an authenticated, HTTP-only session
cookie; protected endpoints derive the user ID and role from that session and
never trust a client-supplied owner ID. Error responses use
`{ "code": "...", "message": "..." }`.

| Method | Path | Input | Success output | Error codes | M1 enforcement / ERD mapping |
| ------ | ---- | ----- | -------------- | ----------- | ---------------------------- |
| POST | `/api/auth/register` | `{ fullName, email, password, phone? }` | `201 { userId, role: "USER" }` | `400 INVALID_INPUT`; `409 EMAIL_EXISTS` | Registration always assigns `USER`; stores `Users(FullName, Email, PasswordHash, Phone, Role)`. Password is hashed and never returned. |
| POST | `/api/auth/login` | `{ email, password }` | `200 { userId, role }` and session cookie | `400 INVALID_INPUT`; `401 INVALID_CREDENTIALS` | Resolves role from `Users(Email, PasswordHash, Role)`; the client cannot choose a role. |
| GET | `/api/courts` | Query: `date?`, `startTime?`, `endTime?`, `location?` (date and both times must be supplied together) | `200 [{ courtId, courtName, location, description, pricePerHour, openTime, closeTime, images }]` | `400 INVALID_TIME_RANGE` | US-01: return only `Court.Status = ACTIVE`; when a time range is supplied, exclude overlapping active `Booking` rows and `Court_Block` ranges. Reads `Court(CourtID, CourtName, Location, Description, PricePerHour, OpenTime, CloseTime, Status)`, `Court_Image(CourtID, Url, SortOrder)`, `Booking(CourtID, BookingDate, StartTime, EndTime, Status)`, and `Court_Block(CourtID, BlockDate, StartTime, EndTime)`. |
| GET | `/api/courts/{courtId}` | Path: `courtId` | `200 { courtId, courtName, location, description, pricePerHour, openTime, closeTime, images }` | `400 INVALID_ID`; `404 COURT_NOT_FOUND` | US-02: expose only active public courts. Reads the same `Court` columns as above and `Court_Image(CourtID, Url, SortOrder)`. `Description` is the current ERD field for court condition; there is no separate condition column. |
| GET | `/api/courts/{courtId}/availability` | Query: `date` (required); optional `durationMinutes` (minimum 60) | `200 { courtId, date, slots: [{ startTime, endTime, available }] }` | `400 INVALID_DATE_OR_DURATION`; `404 COURT_NOT_FOUND` | US-03: generate slots within `Court.OpenTime`–`CloseTime`; mark blocked ranges and overlapping `PENDING`, `CONFIRMED`, or `CHECKED_IN` bookings unavailable. Reads `Court`, `Booking(CourtID, BookingDate, StartTime, EndTime, Status)`, and `Court_Block(CourtID, BlockDate, StartTime, EndTime)`. |
| POST | `/api/bookings` | `{ courtId, bookingDate, startTime, endTime }` | `201 { bookingId, status: "PENDING", holdExpiresAt, totalAmount, depositAmount }` | `400 INVALID_INPUT`; `401 UNAUTHENTICATED`; `404 COURT_NOT_FOUND`; `409 SLOT_UNAVAILABLE` or `ACTIVE_BOOKING_LIMIT`; `422 BOOKING_RULE_VIOLATION` | US-04/US-05: in one transaction, recheck availability and reject interval overlap (BR1), enforce BR2 duration/contiguity, create a 10-minute payment hold (BR3), and enforce at most two active upcoming bookings per user (BR6). Inserts `Booking(UserID, CourtID, BookingDate, StartTime, EndTime, TotalAmount, DepositAmount, Status, HoldExpiresAt, CreatedAt)`. The slot remains occupied while the hold is active. |
| POST | `/api/bookings/{bookingId}/payment` | `{ bankAccountId, paymentMethod }` | `200 { bookingId, status: "CONFIRMED", paymentStatus: "SUCCESS", paidAt }` | `401 UNAUTHENTICATED`; `403 NOT_BOOKING_OWNER`; `404 BOOKING_NOT_FOUND`; `409 HOLD_EXPIRED_OR_ALREADY_PAID`; `422 BANK_ACCOUNT_NOT_VERIFIED`; `502 PAYMENT_FAILED` | Completes US-04: require a verified account (BR7); on successful gateway payment, update `Booking.Status` and insert/update `Payment(BookingID, BankAccountID, Amount, PaymentMethod, TransactionCode, Status, PaidAt)`. Schedule the BR5 reminder in `Notification(UserID, BookingID, ScheduledAt, Type)` using `Booking.ReminderOffsetMinutes`. |
| POST | `/api/bank-accounts` | `{ bankName, accountNumber, accountHolderName }` | `201 { bankAccountId, bankName, accountNumberLast4, verificationStatus: "PENDING" }` | `400 INVALID_INPUT`; `401 UNAUTHENTICATED`; `409 BANK_ACCOUNT_EXISTS` | BR7: link an account to the authenticated user and start OTP verification. Inserts `BankAccount(UserID, BankName, AccountNumber, AccountHolderName, IsVerified)` and `BankAccountVerification(BankAccountID, OTPHash, ExpiresAt, AttemptCount, Status)`. Never return the full account number or OTP hash. |
| POST | `/api/bank-accounts/{bankAccountId}/verify` | `{ otp }` | `200 { bankAccountId, isVerified: true, verifiedAt }` | `400 INVALID_OTP`; `401 UNAUTHENTICATED`; `403 NOT_ACCOUNT_OWNER`; `404 BANK_ACCOUNT_NOT_FOUND`; `409 VERIFICATION_EXPIRED_OR_LOCKED` | BR7: validate expiry and attempt limit, then update `BankAccount.IsVerified/VerifiedAt` and `BankAccountVerification.AttemptCount/VerifiedAt/Status`. |
| DELETE | `/api/bookings/{bookingId}` | Path: `bookingId`; optional body `{ cancelReason }` | `200 { bookingId, status: "CANCELLED", refundAmount, paymentStatus }` | `401 UNAUTHENTICATED`; `403 NOT_BOOKING_OWNER`; `404 BOOKING_NOT_FOUND`; `409 BOOKING_NOT_CANCELLABLE` | US-06 is P1, not P0. Enforce BR4 refund policy and release the slot; update `Booking(Status, CancelledAt, CancelledBy, CancelReason)` and `Payment(Status, RefundAmount, RefundedAt)`. A cancelled booking's scheduled reminder must not be sent (BR5). |
| POST | `/api/manager/court-requests` | `{ requestType: "CREATE", courtName, location, description?, pricePerHour, openTime, closeTime, images? }` | `201 { requestId, status: "PENDING" }` | `400 INVALID_INPUT`; `401 UNAUTHENTICATED`; `403 MANAGER_REQUIRED`; `422 COURT_REQUEST_RULE_VIOLATION` | Manager add-court flow (P1 screen): enforce manager ownership and require Admin approval before public listing; insert `Court_Request(ManagerID, RequestType, CourtName, Location, Description, PricePerHour, OpenTime, CloseTime, Status)` and optional `Court_Request_Image(RequestID, Url, SortOrder)`. |
| POST | `/api/admin/court-requests/{requestId}/review` | `{ decision: "APPROVED" | "REJECTED", rejectReason? }` | `200 { requestId, status, reviewedBy, reviewedAt, courtId? }` | `400 INVALID_DECISION`; `401 UNAUTHENTICATED`; `403 ADMIN_REQUIRED`; `404 REQUEST_NOT_FOUND`; `409 REQUEST_ALREADY_REVIEWED` | Admin approval flow (admin screen is P2): enforce Admin review; update `Court_Request(Status, RejectReason, ReviewedBy, ReviewedAt)`. On approved CREATE, insert `Court(ManagerID, CourtName, Location, Description, PricePerHour, OpenTime, CloseTime, Status = ACTIVE)` and copy request photos into `Court_Image(CourtID, Url, SortOrder)`. |

**Coverage of P0 stories:**

The M1 backlog in `docs/requirements.md` marks US-01 through US-05 as P0.

| P0 story | Endpoint(s) | Coverage |
| -------- | ----------- | -------- |
| US-01 — View available courts | `GET /api/courts` | Lists active courts and can filter by requested date/time availability. |
| US-02 — View court details | `GET /api/courts/{courtId}` | Returns price, photos, location, and description/court condition. |
| US-03 — View available time slots | `GET /api/courts/{courtId}/availability` | Returns the court's slots with unavailable periods identified. |
| US-04 — Book one available time slot | `POST /api/bookings`; `POST /api/bookings/{bookingId}/payment`; bank-account link/verify endpoints | Creates a temporary hold, verifies the payment account, then confirms the booking after successful payment. |
| US-05 — Prevent double booking | `POST /api/bookings`; `GET /api/courts/{courtId}/availability` | Availability is shown before booking; the booking transaction is authoritative and rejects concurrent overlapping requests with `409 SLOT_UNAVAILABLE`. |

**Backlog priority note:** US-06 (cancellation) is P1 in the user-story backlog, even though the `/my-bookings` screen is marked P0 in the M1 screen table. Cancellation is specified above because the task explicitly requests it; this API design does not reclassify US-06. Manager court requests are P1 and Admin court management is P2 in the screen table, so those example endpoints are additional to P0 coverage.

---

## 4. Walking skeleton

- **Route:** `GET /<path>`
- **Table read:** `<table>` (<N> rows seeded from `<data file>`)
- **Configuration:** `.env.example` is committed; real values go in `.env` (never committed).
- **Full installation steps:** see [docs/SETUP.md](SETUP.md).

**Screenshot of the running page:**

![Walking skeleton](images/skeleton.png)

**Query behind the page:**

```sql
SELECT <columns> FROM <table> WHERE <condition> ORDER BY <column>;
```

---

## 5. Design decisions

### Decision 1: <title>

- **Options considered:** <option A> · <option B> · <option C>
- **Chosen:** <option>
- **Why:** <reason tied to the project's constraints>
- **What would change our mind:** <a concrete, testable condition>

### Decision 2: <title>

- **Options considered:** <option A> · <option B>
- **Chosen:** <option>
- **Why:** <reason>
- **What would change our mind:** <condition>

---

## 6. What changed since M1

### Change 1: <short title>

- **What changed:** <requirement / user story / rule that was modified>
- **Why:** <feedback source and reasoning>
- **Related issue:** #<n>

### Change 2: <short title>

- **What changed:** <...>
- **Why:** <...>
- **Related issue:** #<n>
