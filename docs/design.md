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

#### `User`: Stores all user accounts and their roles in the SmashGo system.

| Column    | Type         | PK  | FK  | Constraint                                                 | Enforces (M1 rule)     |
| --------- | ------------ | --- | --- | ---------------------------------------------------------- | ---------------------- |
| UserID    | INTEGER      | ✔   |     | `PRIMARY KEY`, `AUTO_INCREMENT`                            |                        |
| FullName  | VARCHAR(100) |     |     | `NOT NULL`                                                 |                        |
| Email     | VARCHAR(150) |     |     | `NOT NULL`, `UNIQUE`                                       |                        |
| Password  | VARCHAR(255) |     |     | `NOT NULL`                                                 |                        |
| Phone     | VARCHAR(20)  |     |     |                                                            |                        |
| Role      | VARCHAR(20)  |     |     | `NOT NULL`, `CHECK (Role IN ('USER', 'MANAGER', 'ADMIN'))` | Access rules, BR6, BR7 |
| CreatedAt | DATETIME     |     |     | `NOT NULL`                                                 |                        |

`Role` determines whether an account acts as a User, Manager, or Admin. Self-registration creates only accounts with role `USER`; Manager and Admin accounts are provisioned separately. Access to protected functions is controlled according to the user's role.

---

#### `Court`: Stores badminton court information, ownership, availability status, and hourly price.

| Column       | Type          | PK  | FK            | Constraint                                             | Enforces (M1 rule)     |
| ------------ | ------------- | --- | ------------- | ------------------------------------------------------ | ---------------------- |
| CourtID      | INTEGER       | ✔   |               | `PRIMARY KEY`, `AUTO_INCREMENT`                        |                        |
| ManagerID    | INTEGER       |     | `User.UserID` | `NOT NULL`                                             | Manager ownership rule |
| CourtName    | VARCHAR(100)  |     |               | `NOT NULL`                                             | US-10                  |
| Location     | VARCHAR(255)  |     |               | `NOT NULL`                                             | US-10                  |
| Description  | TEXT          |     |               |                                                        |                        |
| PricePerHour | DECIMAL(10,2) |     |               | `NOT NULL`, `CHECK (PricePerHour >= 0)`                | US-10                  |
| Status       | VARCHAR(20)   |     |               | `NOT NULL`, `CHECK (Status IN ('ACTIVE', 'INACTIVE'))` | Court disable rule     |
| CreatedAt    | DATETIME      |     |               | `NOT NULL`                                             |                        |

`ManagerID` identifies the Manager who owns the court. A Manager can only view, add, edit, and disable their own courts. Admin can manage courts across all Managers. A court with upcoming bookings cannot be disabled.

---

#### `Booking`: Records a user's reservation for a specific court, date, and time interval.

| Column        | Type          | PK  | FK              | Constraint                                                                         | Enforces (M1 rule) |
| ------------- | ------------- | --- | --------------- | ---------------------------------------------------------------------------------- | ------------------ |
| BookingID     | INTEGER       | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`                                                    |                    |
| UserID        | INTEGER       |     | `User.UserID`   | `NOT NULL`                                                                         | BR6                |
| CourtID       | INTEGER       |     | `Court.CourtID` | `NOT NULL`                                                                         | BR1, BR2           |
| BookingDate   | DATE          |     |                 | `NOT NULL`                                                                         | BR1, BR2, BR3      |
| StartTime     | TIME          |     |                 | `NOT NULL`                                                                         | BR1, BR2, BR3, BR5 |
| EndTime       | TIME          |     |                 | `NOT NULL`, `CHECK (EndTime > StartTime)`                                          | BR1, BR2           |
| TotalAmount   | DECIMAL(10,2) |     |                 | `NOT NULL`, `CHECK (TotalAmount >= 0)`                                             |                    |
| DepositAmount | DECIMAL(10,2) |     |                 | `NOT NULL`, `CHECK (DepositAmount >= 0)`                                           | BR4                |
| Status        | VARCHAR(20)   |     |                 | `NOT NULL`, `CHECK (Status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED'))` | BR3, BR4, BR6      |
| CreatedAt     | DATETIME      |     |                 | `NOT NULL`                                                                         | BR3                |
| HoldExpiresAt | DATETIME      |     |                 |                                                                                    | BR3                |

`Booking` is the central entity connecting a User and a Court. `HoldExpiresAt` records the 10-minute payment-hold deadline. The booking must be automatically cancelled when the payment deadline is exceeded.

BR1 and BR2 are interval-based business rules and cannot be fully enforced by a simple `UNIQUE` constraint. The system must validate overlapping time intervals and the minimum one-hour/contiguous-slot requirements using transaction, locking, trigger, or application/service logic.

---

#### `Payment`: Records the payment transaction for a booking using a verified bank account.

| Column          | Type          | PK  | FK                          | Constraint                                                                   | Enforces (M1 rule) |
| --------------- | ------------- | --- | --------------------------- | ---------------------------------------------------------------------------- | ------------------ |
| PaymentID       | INTEGER       | ✔   |                             | `PRIMARY KEY`, `AUTO_INCREMENT`                                              |                    |
| BookingID       | INTEGER       |     | `Booking.BookingID`         | `NOT NULL`, `UNIQUE`                                                         | BR3, BR4           |
| BankAccountID   | INTEGER       |     | `BankAccount.BankAccountID` | `NOT NULL`                                                                   | BR7                |
| Amount          | DECIMAL(10,2) |     |                             | `NOT NULL`, `CHECK (Amount >= 0)`                                            |                    |
| PaymentMethod   | VARCHAR(30)   |     |                             | `NOT NULL`                                                                   | BR7                |
| TransactionCode | VARCHAR(100)  |     |                             | `UNIQUE`                                                                     |                    |
| Status          | VARCHAR(20)   |     |                             | `NOT NULL`, `CHECK (Status IN ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED'))` | BR3, BR4, BR7      |
| RefundAmount    | DECIMAL(10,2) |     |                             | `CHECK (RefundAmount >= 0)`                                                  | BR4                |
| PaidAt          | DATETIME      |     |                             |                                                                              | BR3                |
| RefundedAt      | DATETIME      |     |                             |                                                                              | BR4                |

Each booking can have at most one payment record in the current model. Payment is allowed only after the user has successfully linked and verified a bank account.

`RefundAmount` and `RefundedAt` support the cancellation/refund policy in BR4.

---

#### `BankAccount`: Stores bank accounts linked to user accounts for payment.

| Column            | Type         | PK  | FK            | Constraint                      | Enforces (M1 rule) |
| ----------------- | ------------ | --- | ------------- | ------------------------------- | ------------------ |
| BankAccountID     | INTEGER      | ✔   |               | `PRIMARY KEY`, `AUTO_INCREMENT` |                    |
| UserID            | INTEGER      |     | `User.UserID` | `NOT NULL`                      | BR7                |
| BankName          | VARCHAR(100) |     |               | `NOT NULL`                      | BR7                |
| AccountNumber     | VARCHAR(50)  |     |               | `NOT NULL`                      | BR7                |
| AccountHolderName | VARCHAR(150) |     |               | `NOT NULL`                      | BR7                |
| IsVerified        | BOOLEAN      |     |               | `NOT NULL`, `DEFAULT FALSE`     | BR7                |
| VerifiedAt        | DATETIME     |     |               |                                 | BR7                |
| CreatedAt         | DATETIME     |     |               | `NOT NULL`                      |                    |

A User can link one or more bank accounts. A bank account must be verified before it can be used for payment.

---

#### `BankAccountVerification`: Stores OTP verification attempts for linked bank accounts.

| Column         | Type         | PK  | FK                          | Constraint                                                                   | Enforces (M1 rule) |
| -------------- | ------------ | --- | --------------------------- | ---------------------------------------------------------------------------- | ------------------ |
| VerificationID | INTEGER      | ✔   |                             | `PRIMARY KEY`, `AUTO_INCREMENT`                                              |                    |
| BankAccountID  | INTEGER      |     | `BankAccount.BankAccountID` | `NOT NULL`                                                                   | BR7                |
| OTPHash        | VARCHAR(255) |     |                             | `NOT NULL`                                                                   | BR7                |
| ExpiresAt      | DATETIME     |     |                             | `NOT NULL`                                                                   | BR7                |
| VerifiedAt     | DATETIME     |     |                             |                                                                              | BR7                |
| Status         | VARCHAR(20)  |     |                             | `NOT NULL`, `CHECK (Status IN ('PENDING', 'VERIFIED', 'FAILED', 'EXPIRED'))` | BR7                |
| CreatedAt      | DATETIME     |     |                             | `NOT NULL`                                                                   | BR7                |

This table records the OTP verification process. Payment must not proceed unless the corresponding bank account has a successful verification.

---

#### `Notification`: Stores notifications and scheduled booking reminders sent to users.

| Column         | Type         | PK  | FK                  | Constraint                                                                             | Enforces (M1 rule) |
| -------------- | ------------ | --- | ------------------- | -------------------------------------------------------------------------------------- | ------------------ |
| NotificationID | INTEGER      | ✔   |                     | `PRIMARY KEY`, `AUTO_INCREMENT`                                                        |                    |
| UserID         | INTEGER      |     | `User.UserID`       | `NOT NULL`                                                                             | BR5                |
| BookingID      | INTEGER      |     | `Booking.BookingID` |                                                                                        | BR5                |
| Title          | VARCHAR(150) |     |                     | `NOT NULL`                                                                             |                    |
| Message        | TEXT         |     |                     | `NOT NULL`                                                                             |                    |
| Type           | VARCHAR(30)  |     |                     | `NOT NULL`, e.g. `BOOKING_REMINDER`, `BOOKING_CONFIRMATION`, `CANCELLATION`, `PAYMENT` | BR5                |
| IsRead         | BOOLEAN      |     |                     | `NOT NULL`, `DEFAULT FALSE`                                                            |                    |
| ScheduledAt    | DATETIME     |     |                     |                                                                                        | BR5                |
| SentAt         | DATETIME     |     |                     |                                                                                        | BR5                |
| CreatedAt      | DATETIME     |     |                     | `NOT NULL`                                                                             |                    |

For a booking reminder, `ScheduledAt` is set to 4 hours before the booking's start time. Cancelled bookings must not trigger their scheduled reminder.

---

#### `CheckIn`: Records successful or rejected check-in attempts for a booking.

| Column      | Type        | PK  | FK                  | Constraint                                                 | Enforces (M1 rule) |
| ----------- | ----------- | --- | ------------------- | ---------------------------------------------------------- | ------------------ |
| CheckInID   | INTEGER     | ✔   |                     | `PRIMARY KEY`, `AUTO_INCREMENT`                            |                    |
| BookingID   | INTEGER     |     | `Booking.BookingID` | `NOT NULL`, `UNIQUE`                                       | US-09              |
| UserID      | INTEGER     |     | `User.UserID`       | `NOT NULL`                                                 | US-09              |
| CourtID     | INTEGER     |     | `Court.CourtID`     | `NOT NULL`                                                 | US-09              |
| CheckedInAt | DATETIME    |     |                     | `NOT NULL`                                                 | US-09              |
| Status      | VARCHAR(20) |     |                     | `NOT NULL`, `CHECK (Status IN ('CHECKED_IN', 'REJECTED'))` | US-09              |
| CreatedAt   | DATETIME    |     |                     | `NOT NULL`                                                 | US-09              |

A check-in is accepted only when the User has a valid confirmed booking for the selected court and time. An invalid check-in attempt must not create a valid check-in record.

---

#### `Court_Report`: Records reports submitted by users about badminton courts.

| Column      | Type         | PK  | FK              | Constraint                                                                      | Enforces (M1 rule) |
| ----------- | ------------ | --- | --------------- | ------------------------------------------------------------------------------- | ------------------ |
| ReportID    | INTEGER      | ✔   |                 | `PRIMARY KEY`, `AUTO_INCREMENT`                                                 |                    |
| UserID      | INTEGER      |     | `User.UserID`   | `NOT NULL`                                                                      |                    |
| CourtID     | INTEGER      |     | `Court.CourtID` | `NOT NULL`                                                                      |                    |
| Reason      | VARCHAR(150) |     |                 | `NOT NULL`                                                                      |                    |
| Description | TEXT         |     |                 |                                                                                 |                    |
| Status      | VARCHAR(20)  |     |                 | `NOT NULL`, `CHECK (Status IN ('PENDING', 'REVIEWED', 'RESOLVED', 'REJECTED'))` |                    |
| CreatedAt   | DATETIME     |     |                 | `NOT NULL`                                                                      |                    |

A User can submit reports associated with a specific Court. The report status records the progress of the report through the management process.

---

#### `Court_Request`: Stores court creation or management requests submitted by Managers and reviewed by Admins.

| Column       | Type          | PK  | FK            | Constraint                                                          | Enforces (M1 rule)     |
| ------------ | ------------- | --- | ------------- | ------------------------------------------------------------------- | ---------------------- |
| RequestID    | INTEGER       | ✔   |               | `PRIMARY KEY`, `AUTO_INCREMENT`                                     |                        |
| ManagerID    | INTEGER       |     | `User.UserID` | `NOT NULL`                                                          | Manager ownership rule |
| CourtName    | VARCHAR(100)  |     |               | `NOT NULL`                                                          |                        |
| Location     | VARCHAR(255)  |     |               | `NOT NULL`                                                          |                        |
| Description  | TEXT          |     |               |                                                                     |                        |
| PricePerHour | DECIMAL(10,2) |     |               | `NOT NULL`, `CHECK (PricePerHour >= 0)`                             |                        |
| Reason       | TEXT          |     |               |                                                                     |                        |
| Status       | VARCHAR(20)   |     |               | `NOT NULL`, `CHECK (Status IN ('PENDING', 'APPROVED', 'REJECTED'))` |                        |
| ReviewedBy   | INTEGER       |     | `User.UserID` |                                                                     | Admin review rule      |
| CreatedAt    | DATETIME      |     |               | `NOT NULL`                                                          |                        |
| ReviewedAt   | DATETIME      |     |               |                                                                     |                        |

`ManagerID` identifies the Manager who submits the request. `ReviewedBy` identifies the Admin who reviews the request. The referenced `User` for `ManagerID` must have role `MANAGER`, while the referenced `User` for `ReviewedBy` must have role `ADMIN`.

---

## 3. API design

| Method | Path         | Input          | Success        | Error codes                 |
| ------ | ------------ | -------------- | -------------- | --------------------------- |
| GET    | `/api/<...>` | <query params> | 200 · <output> | 400 <reason>                |
| POST   | `/api/<...>` | <body fields>  | 201 · <output> | 401 <reason> · 409 <reason> |

**Coverage of P0 stories:**

| P0 story | Endpoint(s)   |
| -------- | ------------- |
| US<xx>   | <method path> |

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
