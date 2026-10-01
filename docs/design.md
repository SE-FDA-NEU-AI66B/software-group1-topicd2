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

![ERD](images/erd.png)

### 2.2 Table descriptions

#### `<table_1>`: <one-line purpose>

| Column   | Type    | PK  | FK  | Constraint                  | Enforces (M1 rule) |
| -------- | ------- | --- | --- | --------------------------- | ------------------ |
| id       | INTEGER | ✔   |     |                             |                    |
| <column> | <type>  |     |     | <UNIQUE / CHECK / NOT NULL> | <BR#>              |

#### `<table_2>`: <one-line purpose>

| Column   | Type    | PK  | FK         | Constraint | Enforces (M1 rule) |
| -------- | ------- | --- | ---------- | ---------- | ------------------ |
| id       | INTEGER | ✔   |            |            |                    |
| <column> | <type>  |     | <table>.id |            | <BR#>              |

#### `<table_3>`: <one-line purpose>

| Column | Type    | PK  | FK  | Constraint | Enforces (M1 rule) |
| ------ | ------- | --- | --- | ---------- | ------------------ |
| id     | INTEGER | ✔   |     |            | <BR#>              |

#### `<table_4>`: <one-line purpose>

| Column | Type    | PK  | FK  | Constraint | Enforces (M1 rule) |
| ------ | ------- | --- | --- | ---------- | ------------------ |
| id     | INTEGER | ✔   |     |            | <BR#>              |

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
