# Sports Booking Platform

Sports field booking platform for players, helping to find a field, choose a time slot and book quickly, while avoiding double bookings and sending reminders before the game schedule.

**Group:** D2 ·
**Member:**

- Chu Vu Thao Hien - @dqchien
- Phan Thi Anh Quynh - @quynhquynh-blip
- Bui Phuong Thao - @Buithaoaineu
  **Product Owner (fixed for the whole period):** @dqchien
  **Scrum Master (rotating every sprint):** @dqchien (Sprint 1)
  **Board:** [<link>](https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24)

## Test run

> **Implementation is under development.**
>
> Source code, installation instructions, database setup, and application execution commands will be added when the implementation phase begins.

Users need to perform the above steps one by one to install and run the application on the new device.

## 1. Product description

Sports Booking Platform is an online sports stadium booking system. Users can view the list of courses, check available time slots, reserve courses and receive calendar reminders.

The system focuses on solving the problem of manual field booking, difficulty in checking available schedules, and especially the situation of many people booking the same time slot.

### User object

- **Customers not logged in:** see list of courses, course information and available time frames.
- **Users:** find courses, reserve courses, view booked schedules, cancel schedules and receive calendar reminders.
- **Administrator:** manages courses, time frames, booking schedules and tracks usage statistics.

## 2. Main function

### Guest

- See list of sports fields.
- View detailed information of the course.
- See available time slots.
- Register/login account.

### User

- Search and select yard.
- View available calendars by date and time frame.
- Set pitch.
- View your own booking schedule.
- Cancel the booking according to regulations.
- Receive notifications/reminders before play time.

### Admin

- Add, edit, delete and manage courses.
- Manage operating hours.
- View and manage bookings.
- Check yard condition.
- View usage frequency statistics by time frame.

## 3. Business rules

### Anti-duplication

A yard is only allowed to have a maximum of one booking in the same time frame.

When a user confirms a course reservation, the system must check the availability of the time slot before creating the booking.

If another user has already booked that time slot, the system must reject the new booking and notify that the time slot is no longer available.

Checking and booking must be handled in a way that ensures two people cannot simultaneously successfully book the same course and time slot.

### Calendar management

Each booking contains a minimum of:

- Placer.
- Yard.
- Play date.
- Start time.
- End time.
- Booking status.

Statuses may include:

- `Confirmed`
- `Cancelled`
- `Completed`

### Notice

The system sends notifications to remind users before the pitch reservation time.

For example:

> "You have a reservation scheduled for 6:00 p.m. today. Please arrive on time."

## 4. Data and statistics

The system stores information about courses, users and booking schedules for management and analysis.

Booking data is used for statistics:

- Number of field reservations by day.
- Frequency of use by time frame.
- Time frame with the most bookings.
- Rarely used time frame.
- Frequency of use of each yard.

For example, the system may detect that the time slot **18:00–20:00** has higher demand than other time slots.

## 5. Industry challenges

### Concurrent Booking

This is the main technical challenge of the system.

If two people book the same course and time frame at the same time, the system must ensure that only one booking is successfully created.

Possible solutions:

- Database constraint / unique constraint.
- Transactions.
- Check availability before booking.
- Handle errors when bookings are duplicated.

### Schedule Management

The system must manage the date, start time, end time and status of each booking.

Need to ensure:

- Booking a time slot that is already in use is not allowed.
- End time before start time is not allowed.
- Bookings are not allowed during times when the yard is not operating.
- Accurately handle canceled bookings.

### Notifications

The system needs to determine when to send reminders based on the booking time.

For example:

- Reminder 24 hours in advance.
- Reminder 1 hour in advance.

The notification mechanism needs to avoid duplicate sending or sending notifications for canceled bookings.

## 6. Decentralization

The system has three main roles:

| Role  | Main rights                             |
| ----- | --------------------------------------- |
| Guest | View stadium and time frame             |
| User  | Book, view and cancel your booking      |
| Admin | Yard management, booking and statistics |

Users are only allowed to edit or cancel bookings under their account.

Admin has the right to manage all booking and yard data.

## 7. Project scope

### Within range

- User account management.
- Sports field management.
- View schedules and available time slots.
- Set pitch.
- Anti-duplication.
- Cancel booking.
- Calendar reminder notification.
- Statistics on usage frequency by time frame.

### Out of range

- Actual online payments.
- Integrated bank payment gateway.
- Court rating system.
- AI-based court recommendations.
- Integration of maps and real-time location tracking.

Out-of-scope functions may be considered as extended features if time permits.

## 8. Testing

Key test cases focus on critical business logic:

- Booking an available time slot.
- Two users attempting to book the same slot simultaneously.
- Booking a slot that is already reserved.
- Canceling a booking.
- Booking an invalid time slot.
- Verifying User and Admin access rights.
- Verifying reminder notifications.
- Verifying usage frequency statistics.

In particular, the system must ensure coverage of **concurrent booking** test cases: when multiple requests attempt to book the same slot, the system must prevent a situation where a single slot holds multiple valid bookings.
