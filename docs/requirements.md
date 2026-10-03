# Milestone 1 - Requirements Document

**Team:** Team 01 - SmashGo

**Topic:** D2 - Sports Platform

**Members:**

- Chử Vũ Thảo Hiền
- Phan Thị Anh Quỳnh
- Bùi Phương Thảo

**Product Owner:** @dqchien

**Scrum Master:** @quynhquynh-blip (Sprint 1)

**Repository:** https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2.git

**Project board:** https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24

**Submitted by:** Chử Vũ Thảo Hiền

---

<img src="../images/Sprint Planning.png" alt="Sprint Planning" width="500">
<img src="../images/Final Sprint 1.png" alt="Final Sprint 1" width="500">

---

## 1. Product vision

SmashGo is a system that enables badminton players of all levels to book courts for their desired time slots and secure a reservation in just minutes. This eliminates the need for manual methods - such as calling or visiting the facility to speak with the manager - which fail to provide real-time availability updates and often lead to scheduling conflicts between groups.

## 2. Personas

**Lê Sỹ Huy – 20-year-old third-year student and recreational badminton player.**

- Plays badminton with friends about four times a week; usually the one who books the court for the group. Typically plays in the 8:00 PM – 10:00 PM slot at familiar venues like Maxping Vĩnh Tuy and Phúc Long Badminton Court.
- **Goal:** To book courts faster, guarantee availability, and avoid missing a session due to a busy schedule.
- **Blocked by:** Needs immediate access to comprehensive information—price, availability, court conditions, and location—to make quick decisions; also requires the ability to remind schedule the booking in advance (around 4 hours prior to play).
- **In his words:** "I find the way the app I'm currently using (ALOBO) works to be satisfactory."
- **Interview note:** Interviewed at 2:00 PM – 2:10 PM on September 16, 2026.

**Chử Vũ Thảo Hiền – 20-year-old third-year university student and recreational badminton player.**

- Plays badminton with friends about three times a week; previously responsible for booking courts for the club. Usually plays from 3:00 PM to 5:00 PM at Đức Thảo Badminton Court (18 Tam Trinh). Before discovering the ALOBO app, I used to book courts by messaging the owner via Zalo, which often led to scheduling conflicts with other groups.
- **Goal:** To book a court quickly, secure a confirmed reservation, and ensure there are no overlaps with other groups.
- **Blocked by:** Needs access to comprehensive information—actual photos of the court, pricing, availability, court condition, and location.
- **In my words:** "Booking a court used to be complicated and risky before I found the ALOBO app. However, since using the app, I’ve found the process to be smooth and trouble-free."
- **Interview note:** Based on personal experience.

**Nguyễn Minh Đức – 35-year-old badminton court owner and manager.**

- Manages a badminton facility with several courts and handles reservations, customer inquiries, and daily court operations. Currently relies on phone calls, Zalo messages, and manually maintained schedules to organize bookings.
- **Goal:** To manage court availability efficiently, keep booking information up to date, and prevent scheduling conflicts while increasing the number of successful reservations.
- **Blocked by:** Needs a centralized system to update court information, confirm or cancel reservations, monitor booking status, and view usage frequency by time slot; manual management makes it difficult to track changes and avoid double bookings.
- **In his words:** "Managing reservations manually takes a lot of time, and overlapping bookings can happen when several customers contact us at the same time."
- **Interview note:** Assumed interview with a badminton court owner and manager on September 17, 2026.

## 3. Scenarios

**Scenario 1 — Lê Sỹ Huy: Quickly booking a familiar court**

1. Lê Sỹ Huy decides to play badminton with his friends at 8:00 PM and needs to arrange the court before the evening.
2. He searches for courts that are available at the desired time and checks the basic information, including price, location, and court condition.
3. Since he usually plays at familiar venues, he chooses a court he has played at before.
4. He selects the 8:00 PM–10:00 PM time slot and verifies that it is available.
5. He provides the required information and confirms the reservation.
6. The system records the booking and provides the confirmed reservation details.
   7.Huy schedules a reminder for around four hours before the session so he can remember the booking despite his busy schedule.
7. Before leaving for the session, he checks the reminder and reservation details, then goes to the court with his friends.

**Scenario 2 — Chử Vũ Thảo Hiền: Finding a suitable court and avoiding booking conflicts**

1. Chử Vũ Thảo Hiền needs to arrange a badminton court for her group for an upcoming session from 3:00 PM to 5:00 PM.
2. Because she previously experienced scheduling conflicts when booking through Zalo, she first looks for courts with clearly confirmed availability.
3. She examines several available options and checks their actual photos, prices, court conditions, and locations before making a decision.
4. She finds a suitable court at Đức Thảo Badminton Court and checks whether the desired 3:00 PM–5:00 PM period is available.
5. After confirming the available time, she enters the required information and submits the reservation.
6. The system confirms the reservation and provides the booking details, including the selected court and time.
7. Hiền checks the confirmation to make sure her group's reservation has been successfully recorded and does not overlap with another booking.
8. On the scheduled day, she and her friends arrive at the reserved court and play at the confirmed time.

**Scenario 3 — Nguyễn Minh Đức: Managing courts and reservations in one place**

1. Nguyễn Minh Đức starts his day by signing in to the system to check his courts and the reservations for the day, instead of going through phone calls and Zalo messages.
2. He sees the current booking status of each of his courts and notices that one court needs to be closed for maintenance, so he updates the court information and marks it as unavailable for customers.
3. When several customers try to book the same time slot at almost the same time, the system accepts only one reservation and shows the slot as taken for the others, so Đức does not have to sort out overlapping bookings by hand.
4. He reviews the new reservations, confirms the valid ones, and cancels a booking when a customer asks to change their plan, which makes that time slot available again.
5. He checks that the court information and availability shown to customers are up to date, so players always see accurate schedules without having to contact him.
6. At the end of the week, he reviews how often each time slot was booked, sees which hours are busy and which are empty, and uses this to plan how to get more successful reservations.
## 4. User Stories

### User Stories
| ID    | Story                                                                                                                                                                         | Priority | Points |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -----: |
| US-01 | As a user, I want to view available badminton courts so that I can find a suitable court for my session.                                                                      | P0       |      3 |
| US-02 | As a user, I want to view detailed court information, including price, photos, location, and court condition, so that I can choose a suitable court.                          | P0       |      3 |
| US-03 | As a user, I want to view available time slots for a court so that I can select a suitable playing time.                                                                      | P0       |      3 |
| US-04 | As a user, I want to book one available time slot so that I can secure a badminton court for my group.                                                                        | P0       |      5 |
| US-05 | As a user, I want the system to prevent double booking so that my reservation does not overlap with another user's booking.                                                   | P0       |      5 |
| US-06 | As a user, I want to cancel my booking so that I can release a court when I no longer need it.                                                                                | P1       |      3 |
| US-07 | As a user, I want to receive a booking reminder so that I do not forget my scheduled badminton session.                                                                       | P1       |      3 |
| US-08 | As a user, I want to view my booking history so that I can check my previous and upcoming reservations.                                                                       | P1       |      3 |
| US-09 | As a user, I want to check in for my booking so that the system can record that I have arrived and used the court.                                                            | P1       |      3 |

### Admin Stories
| ID    | Story                                                                                                                                                                         | Priority | Points |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -----: |
| US-10 | As an administrator, I want to view a dashboard showing the total number of badminton courts and commission information so that I can monitor the overall operation of the platform. | P1       |      3 |
| US-11 | As an administrator, I want to activate or deactivate badminton courts so that I can keep court information up to date and control which courts are available for booking. | P0       |      5 |
| US-12 | As an administrator, I want to approve or reject a request to add a badminton court from a manager so that only approved courts are added to the platform. | P0       |      5 |
| US-13 | As an administrator, I want to view badminton court usage frequency by time slot so that I can understand booking patterns and monitor court usage. | P1       |      3 |
| US-14 | As an administrator, I want to filter badminton courts by location, price, and other criteria so that I can find suitable courts for management and recommendation. | P1       |      3 |

### Manager Stories
| ID    | Story                                                                                                                                                                         | Priority | Points |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -----: |
| US-15 | As a manager, I want to add a new badminton court so that I can provide my court for users to book after it is approved by an administrator. | P1       |      5 |
| US-16 | As a manager, I want to edit or delete my own badminton courts so that I can keep my court information up to date. | P1       |      3 |
| US-17 | As a manager, I want to view the status of my court submission so that I know whether my new court is pending, approved, or rejected by an administrator. | P1       |      3 |
| US-18 | As a manager, I want to receive and view reports about my badminton courts from guests or users so that I can identify and address problems with my courts. | P2       |      3 |

### User Stories - Report
| ID    | Story                                                                                                                                                                         | Priority | Points |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -----: |
| US-19 | As a guest or user, I want to report an issue with a badminton court so that the manager of that court is notified and can act on it. | P1       |      5 |


### US-01 — View Available Badminton Courts

**Acceptance Criteria**

1. **Given** badminton courts are available at 8:00 PM,  
   **When** the user searches for courts at 8:00 PM,  
   **Then** the system displays the available courts for that time.

2. **Given** a court has no available slots at 8:00 PM–10:00 PM,  
   **When** the user searches for courts during this period,  
   **Then** the system does not display that court as available.

### US-02 — View Detailed Court Information

**Acceptance Criteria**

1. **Given** a badminton court has information including price, photos, location, and court condition,  
   **When** the user opens the court details,  
   **Then** the system displays all four types of information.

2. **Given** the selected court costs 100,000 VND per hour,  
   **When** the user views the court details,  
   **Then** the system displays the price as 100,000 VND per hour.

### US-03 — View Available Time Slots

**Acceptance Criteria**

1. **Given** a court is available from 3:00 PM to 5:00 PM,  
   **When** the user views the court schedule,  
   **Then** the system displays the 3:00 PM–5:00 PM time slot as available.

2. **Given** the 8:00 PM–10:00 PM time slot has already been booked,  
   **When** the user views the court schedule,  
   **Then** the system displays the 8:00 PM–10:00 PM slot as unavailable.

### US-04 — Book One Available Time Slot

**Acceptance Criteria**

1. **Given** the 8:00 PM–10:00 PM time slot is available,  
   **When** the user confirms the booking for that slot,  
   **Then** the system creates exactly one booking with the status "Confirmed".

2. **Given** the user has selected one available 2-hour time slot,  
   **When** the user submits the required booking information,  
   **Then** the system reserves only the selected court and time slot for that user.

### US-05 — Prevent Double Booking

**Acceptance Criteria**

1. **Given** Court A is already booked from 3:00 PM to 5:00 PM on the selected date,  
   **When** another user attempts to book Court A for the same 3:00 PM–5:00 PM period,  
   **Then** the system rejects the second booking and keeps only one confirmed booking for that slot.

2. **Given** two users submit booking requests for the same court and the same 2-hour time slot at the same time,  
   **When** the system processes both requests,  
   **Then** exactly one request is confirmed and the other request is rejected.

### US-06 — Cancel a Booking

**Acceptance Criteria**

1. **Given** the user has a confirmed booking from 3:00 PM to 5:00 PM,  
   **When** the user cancels the booking,  
   **Then** the booking status changes to "Cancelled".

2. **Given** a booking for the 3:00 PM–5:00 PM slot has been cancelled,  
   **When** another user views the court schedule,  
   **Then** the 3:00 PM–5:00 PM slot is displayed as available for a new booking.

### US-07 — Receive a Booking Reminder

**Acceptance Criteria**

1. **Given** the user's badminton session starts at 8:00 PM,  
   **When** the user sets a reminder for 4 hours before the session,  
   **Then** the system schedules the reminder for 4:00 PM on the same day.

2. **Given** the user has cancelled a booking before the scheduled reminder time,  
   **When** the reminder time is reached,  
   **Then** the system does not send a reminder for the cancelled booking.

### US-08 — View Booking History

**Acceptance Criteria**

1. **Given** the user has made 5 bookings,  
   **When** the user opens the booking history,  
   **Then** the system displays all 5 bookings associated with the user's account.

2. **Given** the user's bookings have statuses such as "Confirmed", "Cancelled", and "Completed",  
   **When** the user views the booking history,  
   **Then** the system displays the correct status for each booking.

### US-09 — Check In for a Booking

**Acceptance Criteria**

1. **Given** the user's booking starts at 8:00 PM,  
   **When** the user checks in at 7:50 PM,  
   **Then** the system records the booking as "Checked-in".

2. **Given** the user does not have a confirmed booking for the selected court and time,  
   **When** the user attempts to check in,  
   **Then** the system rejects the check-in and does not create a check-in record.

### US-10 — View Admin Dashboard

**Acceptance Criteria**

1. **Given** the system contains badminton courts and booking transactions,
   **When** the administrator opens the dashboard,
   **Then** the system displays the total number of badminton courts and commission information.

2. **Given** there are no badminton courts or commission transactions,
   **When** the administrator opens the dashboard,
   **Then** the system displays zero for the corresponding statistics.

### US-11 — Activate or Deactivate Badminton Courts

**Acceptance Criteria**

1. **Given** a badminton court is currently inactive,
   **When** the administrator activates the court,
   **Then** the system changes the court status to active and makes the court available for booking.

2. **Given** a badminton court is currently active,
   **When** the administrator deactivates the court,
   **Then** the system changes the court status to inactive and prevents new bookings for that court.

### US-12 — Approve or Reject Court Request

**Acceptance Criteria**

1. **Given** a manager has submitted a request to add a badminton court,
   **When** the administrator approves the request,
   **Then** the system changes the request status to approved and adds the court to the platform.

2. **Given** a manager has submitted a request to add a badminton court,
   **When** the administrator rejects the request,
   **Then** the system changes the request status to rejected and does not add the court to the platform.

### US-13 — View Court Usage Frequency

**Acceptance Criteria**

1. **Given** the system contains booking records for badminton courts,
   **When** the administrator views court usage frequency,
   **Then** the system displays the number or frequency of bookings for each relevant time slot.

2. **Given** a time slot has no booking records,
   **When** the administrator views court usage frequency,
   **Then** the system displays that there is no recorded usage for that time slot.

### US-14 — Filter and View Court Recommendations

**Acceptance Criteria**

1. **Given** there are badminton courts with different locations and prices,
   **When** the administrator applies a location or price filter,
   **Then** the system displays only the courts matching the selected criteria.

2. **Given** no badminton court matches the selected filters,
   **When** the administrator applies the filters,
   **Then** the system displays that no matching courts are available.

### US-15 — Add New Badminton Court

**Acceptance Criteria**

1. **Given** the manager provides all required badminton court information,
   **When** the manager submits the new court,
   **Then** the system creates a court submission with Pending status and sends it to the administrator for approval. 

2. **Given** a new court submission has Pending status,
   **When** the administrator has not approved it,
   **Then** the court is not displayed publicly and cannot be booked by users.

### US-16 — Edit or Delete Own Badminton Courts

**Acceptance Criteria**

1. **Given** a manager owns a badminton court,
   **When** the manager edits the court information,
   **Then** the system updates the court information successfully.

2. **Given** a manager owns a badminton court,
   **When** the manager deletes the court,
   **Then** the system removes or disables the court according to the system rules.

### US-17— View Court Submission Status

**Acceptance Criteria**

1. **Given** the manager has submitted a new badminton court,
   **When** the manager views the court list,
   **Then** the system displays the submission status as Pending, Approved, or Rejected.

2. **Given** a court submission has Pending status,
   **When** the administrator has not made a decision,
   **Then** the court remains unavailable for public booking.


### US-18 — View Court Reports

**Acceptance Criteria**

1. **Given** a guest or user submits a report about a badminton court owned by the manager,
   **When** the report is submitted,
   **Then** the system associates the report with the corresponding court and manager.

2. **Given** the manager has received reports about their badminton courts,
   **When** the manager views the court information,
   **Then** the system displays the reports related to their own courts.

### US-19 — Report a Court Issue

**Acceptance Criteria**

1. **Given** a guest or user is viewing a badminton court,
   **When** they submit a report with a reason and description,
   **Then** the system creates a report for the selected court and sends it to the manager of that court.

2. **Given** a new report has been submitted,
   **When** the manager views the reports for their courts,
   **Then** the system displays the report with New status.

## 5. Business Rules

| ID  | Rule                                                                                                                                                                            | Worked example                                                                                                                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BR1 | A court cannot be double-booked for a time slot that is already reserved.                                                                                                       | Court 3 (Maxping Vinh Tuy) is already booked for 20:00–22:00. Another user tries to book the same court for 20:00–21:30 → rejected; the system shows "Court 3 is already booked for the 20:00–22:00 slot."                             |
| BR2 | Every booking must last at least 1 hour. If multiple groups play on the same court back-to-back, their bookings must be contiguous — no gap is allowed between them.            | Booking 20:00–21:00 → valid (meets the 1-hour minimum). On Court 1: Group A books 16:00–18:00, Group B books 18:30–... → invalid, because there is a 30-minute gap between the two bookings.                                           |
| BR3 | The slot is held for 10 minutes pending payment; the reservation will be automatically cancelled if this time limit is exceeded.                                                | If a user selects Court 3 for the 20:00–21:00 slot at 18:00, the system holds the reservation until 18:10. If payment is not transferred by 18:10, the slot is automatically released and becomes available for others to book.        |
| BR4 | Cancelling more than 4 hours before play time gets a full refund; cancelling within 4 hours forfeits 50% of the deposit.                                                        | Booking for 20:00, cancelled at 15:00 (5 hours before) → full refund. Cancelled at 17:00 (3 hours before) → only 50% refunded.                                                                                                         |
| BR5 | The system automatically sends a reminder notification 4 hours before play time.                                                                                                | Booking starts at 20:00 → reminder notification is sent at 16:00 the same day.                                                                                                                                                         |
| BR6 | Each account may hold at most 2 active (upcoming) bookings at a time.                                                                                                           | A user already has 2 upcoming bookings (e.g., Sep 16 and Sep 18). Trying to add a 3rd booking → rejected with the message "You already have 2 active bookings — please complete or cancel one before booking another."                 |
| BR7 | Before making a payment, a user must link and verify a bank account. The system validates the account information and only proceeds with payment after successful verification. | The user selects a bank, enters the account number and account holder name, and completes OTP verification. If the information is invalid or verification fails, the system rejects the link and does not process the booking payment. |

## 6. Screens and Navigation Flow

### 6.1 Screen Table

| Route             | Purpose                                               | Access | Priority |
| ----------------- | ----------------------------------------------------- | ------ | -------- |
| `/`               | Browse badminton courts and view court information    | G, U   | P0       |
| `/availability`   | View available courts by date and time                | G, U   | P0       |
| `/login`          | Sign in with email and password (shared by all roles) | G      | P0       |
| `/register`       | Create a new User account                             | G      | P0       |
| `/book`           | Select court, date, time, then link bank and pay      | G, U   | P0       |
| `/my-bookings`    | View and cancel personal bookings                     | U      | P0       |
| `/manager/courts` | Add, edit, or disable **own** courts                  | M      | P1       |
| `/admin/courts`   | Add, edit, or disable any court in the system         | A      | P2       |

**Access:** G = Guest, U = User, M = Manager (court owner), A = Admin

**Login decision (`/login`):**

- One **shared login form** for all 3 roles (User / Manager / Admin). No separate form per role.
- The role is **detected automatically** from the `role` field of the account. The user never picks a role.
- After a successful login, redirect by role:
  - User → back to the page they came from (e.g. `/book`), otherwise `/my-bookings`
  - Manager → `/manager/courts`
  - Admin → `/admin/courts`
- Signed-in users who open `/login` or `/register` are redirected to their default page.
- Guests who open a protected route (`/my-bookings`, `/manager/courts`, `/admin/courts`) are redirected to `/login`.
- A signed-in user who opens a route outside their role gets `403 Forbidden`.

**Registration decision (`/register`):**

- Self-registration only creates accounts with role **User**.
- Manager and Admin accounts are not created through the UI. They are provisioned by Admin or seeded in the database.
- After registering, the user is signed in and redirected like a normal login.

**Access rules for `/manager/courts`:**

- Manager only sees, adds, edits, and disables courts **they own**.
- Manager cannot see or modify courts of another Manager. The list is filtered by `ownerId = currentUser.id` on the backend, not only hidden in the UI.
- Direct access to another Manager's court (by court ID in the URL or API) is rejected with `403 Forbidden`.
- Every court created by a Manager is automatically assigned to that Manager as owner.
- Only Admin (`/admin/courts`) can view and manage courts across all Managers.

**Disable court rule (Manager and Admin):**

- A court that has **upcoming bookings cannot be disabled**. The system shows a message and the court stays active.
- The court can be disabled once all its upcoming bookings are completed or cancelled.

### 6.2 Flow Diagram

#### Guest / User flow

```text
                  ┌───────────────┐
                  │       /       │
                  │ Browse courts │
                  └───────┬───────┘
                          │
                    View / Search
                          ↓
                  ┌───────────────┐
                  │ /availability │◄────────────────┐
                  │ Find a court  │                 │
                  └───────┬───────┘                 │
                          │                         │
                     Select court                   │
                          ↓                         │
                  ┌───────────────┐                 │
                  │     /book     │                 │
                  │  Select date  │                 │
                  │  Select time  │                 │
                  │    Confirm    │                 │
                  └───────┬───────┘                 │
                          │                         │
                  Proceed to payment                │
                          ↓                         │
                  ┌───────────────┐                 │
                  │    /login     │                 │
                  │   Sign in     │                 │
                  │ New? Register │                 │
                  │  (/register)  │                 │
                  └───────┬───────┘                 │
                          │                         │
                   Link bank account                │
                          ↓                         │
                   Verify bank (OTP)                │
                          ↓                         │
                       Payment                      │
                          ↓                         │
                  ┌───────────────┐                 │
                  │ /my-bookings  │                 │
                  │ View / Cancel │                 │
                  └───────┬───────┘                 │
                          │                         │
                      Book again                    │
                          └─────────────────────────┘
```

> `/login` is skipped if the user is already signed in.
> After `/login` or `/register`, the user returns to `/book` with the selected court, date, and time preserved.

#### Manager flow

```text
                  ┌───────────────┐
                  │    /login     │
                  │   Sign in     │
                  └───────┬───────┘
                          │
                   role = Manager
                          ↓
                ┌───────────────────┐
                │  /manager/courts  │
                │  List MY courts   │
                │ (own courts only) │
                └─────────┬─────────┘
                          │
              ┌───────────┼───────────┐
              ↓           ↓           ↓
          Add court    Edit court   Disable court
         (owner = me)  (own only)   (own only)
              │           │           │
              └───────────┼───────────┘
                          │
                     Save changes
                          ↓
                ┌───────────────────┐
                │  /manager/courts  │
                │   Updated list    │
                └─────────┬─────────┘
                          │
                  View updated court
                          ↓
                  ┌───────────────┐
                  │ /availability │
                  └───────────────┘
```

> Opening or editing a court owned by another Manager → `403 Forbidden`, redirect back to `/manager/courts`.
> Disable is blocked if the court has upcoming bookings.

#### Admin flow

```text
                  ┌───────────────┐
                  │    /login     │
                  │   Sign in     │
                  └───────┬───────┘
                          │
                    role = Admin
                          ↓
                  ┌───────────────┐
                  │ /admin/courts │
                  │ Add / Edit /  │
                  │ Disable courts│
                  │ (all courts)  │
                  └───────┬───────┘
                          │
                     Update courts
                          ↓
                  ┌───────────────┐
                  │ /availability │
                  └───────────────┘
```

> Disable is blocked if the court has upcoming bookings.