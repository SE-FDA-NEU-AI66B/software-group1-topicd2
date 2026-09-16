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

**Pull Request:**

**Merge commit:**

**Submitted by:** Chử Vũ Thảo Hiền

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


## 3. Scenarios
**Scenario 1 — Lê Sỹ Huy: Quickly booking a familiar court**
1. Lê Sỹ Huy decides to play badminton with his friends at 8:00 PM and needs to arrange the court before the evening.
2. He searches for courts that are available at the desired time and checks the basic information, including price, location, and court condition.
3. Since he usually plays at familiar venues, he chooses a court he has played at before.
4. He selects the 8:00 PM–10:00 PM time slot and verifies that it is available.
5. He provides the required information and confirms the reservation.
6. The system records the booking and provides the confirmed reservation details.
7.Huy schedules a reminder for around four hours before the session so he can remember the booking despite his busy schedule.
8. Before leaving for the session, he checks the reminder and reservation details, then goes to the court with his friends.

**Scenario 2 — Chử Vũ Thảo Hiền: Finding a suitable court and avoiding booking conflicts**
1. Chử Vũ Thảo Hiền needs to arrange a badminton court for her group for an upcoming session from 3:00 PM to 5:00 PM.
2. Because she previously experienced scheduling conflicts when booking through Zalo, she first looks for courts with clearly confirmed availability.
3. She examines several available options and checks their actual photos, prices, court conditions, and locations before making a decision.
4. She finds a suitable court at Đức Thảo Badminton Court and checks whether the desired 3:00 PM–5:00 PM period is available.
5. After confirming the available time, she enters the required information and submits the reservation.
6. The system confirms the reservation and provides the booking details, including the selected court and time.
7. Hiền checks the confirmation to make sure her group's reservation has been successfully recorded and does not overlap with another booking.
8. On the scheduled day, she and her friends arrive at the reserved court and play at the confirmed time.


## 5. Business Rules

| ID  | Rule                                                                                                                                                                 | Worked example                                                                                                                                                                                                                  |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BR1 | A court cannot be double-booked for a time slot that is already reserved.                                                                                            | Court 3 (Maxping Vinh Tuy) is already booked for 20:00–22:00. Another user tries to book the same court for 20:00–21:30 → rejected; the system shows "Court 3 is already booked for the 20:00–22:00 slot."                      |
| BR2 | Every booking must last at least 1 hour. If multiple groups play on the same court back-to-back, their bookings must be contiguous — no gap is allowed between them. | Booking 20:00–21:00 → valid (meets the 1-hour minimum). On Court 1: Group A books 16:00–18:00, Group B books 18:30–... → invalid, because there is a 30-minute gap between the two bookings.                                    |
| BR3 | The slot is held for 10 minutes pending payment; the reservation will be automatically cancelled if this time limit is exceeded.                                     | If a user selects Court 3 for the 20:00–21:00 slot at 18:00, the system holds the reservation until 18:10. If payment is not transferred by 18:10, the slot is automatically released and becomes available for others to book. |
| BR4 | Cancelling more than 4 hours before play time gets a full refund; cancelling within 4 hours forfeits 50% of the deposit.                                             | Booking for 20:00, cancelled at 15:00 (5 hours before) → full refund. Cancelled at 17:00 (3 hours before) → only 50% refunded.                                                                                                  |
| BR5 | The system automatically sends a reminder notification 4 hours before play time.                                                                                     | Booking starts at 20:00 → reminder notification is sent at 16:00 the same day.                                                                                                                                                  |
| BR6 | Each account may hold at most 2 active (upcoming) bookings at a time.                                                                                                | A user already has 2 upcoming bookings (e.g., Sep 16 and Sep 18). Trying to add a 3rd booking → rejected with the message "You already have 2 active bookings — please complete or cancel one before booking another."          |

## 6. Screens and Navigation Flow

### 6.1 Screen Table

## 6. Screens and Navigation Flow

### 6.1 Screen Table

| Route | Purpose | Access | Priority |
|---|---|---|---|
| `/` | Browse badminton courts and view court information | G, U | P0 |
| `/availability` | View available courts by date and time | G, U | P0 |
| `/book` | Select a court, date, and time, then proceed to booking/payment | G, U | P0 |
| `/my-bookings` | View and cancel personal bookings | U | P0 |
| `/admin/courts` | Add, edit, or disable badminton courts | A | P2 |

**Access:** G = Guest, U = User, A = Admin

### 6.2 Flow Diagram

                  ┌───────────────┐
                  │       /       │
                  │  Browse courts│
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
                  │ Select date   │                 │
                  │ Select time   │                 │
                  │    Confirm    │                 │
                  └───────┬───────┘                 │
                          │                         │
                   Proceed to payment               │
                          ↓                         │
                    ┌───────────┐                   │
                    │  Sign in  │                   │
                    │ if Guest  │                   │
                    └─────┬─────┘                   │
                          │                         │
                       Payment                      │
                          ↓                         │
                  ┌───────────────┐                 │
                  │ /my-bookings  │                 │
                  │ View / Cancel │                 │
                  └───────┬───────┘                 │
                          │                         │
                      Book again                    │
                          └─────────────────────────┘


                  ┌───────────────┐
                  │ /admin/courts │
                  │ Add / Edit /  │
                  │ Disable courts│
                  └───────┬───────┘
                          │
                     Update courts
                          ↓
                  ┌───────────────┐
                  │ /availability │
                  └───────────────┘