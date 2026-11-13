**Live app: https://smashgo-zfdv.onrender.com** · health check: [https://smashgo-zfdv.onrender.com/health](https://smashgo-zfdv.onrender.com/health)

# SmashGo - Sports Booking Platform

[![CI](https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/SE-FDA-NEU-AI66B/software-group1-topicd2/actions/workflows/ci.yml?query=branch%3Amain)

Sports field booking platform for players, helping to find a field, choose a time slot and book quickly, while avoiding double bookings and sending reminders before the game schedule.

> **Free hosting.** The app sleeps after 15 minutes without visitors, so the first visit can take about a minute. The SQLite database is **reset to the sample data at every deploy and restart** (`init_db.py` runs before the app starts), so bookings made while testing do not stay forever.

## Test accounts

Fake accounts from the sample data, for testing only. No real password is used anywhere.

| Role    | Email                                    | Password          |
| ------- | ---------------------------------------- | ----------------- |
| User    | `user@smashgo.local`                     | `UserTest123!`    |
| User 2  | `user2@smashgo.local`                    | `User2Test123!`   |
| Manager | `walking-skeleton-manager@smashgo.local` | `ManagerTest123!` |
| Admin   | `admin@smashgo.local`                    | `AdminTest123!`   |

The bank is simulated. The payment OTP is always `123456`. Any account number can be linked; one ending in `0000` makes the payment fail, to show the error case.

## P0 stories and where each one starts

Every story starts from the first page of the live app and needs only clicks.

| Story | What you can do | Start here |
| ----- | --------------- | ---------- |
| US-01 | View available badminton courts | First page, **Danh sách sân** (`/courts`) |
| US-02 | View court details: price, photos, location, condition | `/courts` → **Chi tiết sân** on a court card |
| US-03 | View free time slots of a court | Court details page → pick a date |
| US-04 | Book one free slot, link a bank account and pay | `/courts` → **Đặt sân →** (log in as User; OTP `123456`) |
| US-05 | The system refuses a double booking | Book **SmashGo Cầu Giấy 1**, tomorrow, 20:00-22:00: the slot is already taken by User 2, so the booking is refused with an explanation |
| US-11 | Admin activates or deactivates a court | Log in as Admin → **Quản lý sân** (`/admin/courts`) |
| US-12 | Admin approves or rejects a request to add a court | Log in as Admin → **Quản lý sân** → pending requests |

## Team

**Group:** 1 · **Topic:** D2

| Member | GitHub |
| ------ | ------ |
| Chu Vu Thao Hien | @dqchien |
| Phan Thi Anh Quynh | @quynhquynh-blip |
| Bui Phuong Thao | @Buithaoaineu |

**Product Owner (fixed for the whole period):** @dqchien

**Scrum Master (rotating every sprint):** Sprint 1: @quynhquynh-blip · Sprint 2: @Buithaoaineu · Sprint 3: @dqchien · Sprint 4: @quynhquynh-blip · **Sprint 5: @Buithaoaineu**

**Board:** https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24 · **Operations:** [docs/operations.md](docs/operations.md)

## First screen

![SmashGo court discovery first screen](images/1st%20screen.PNG)

**Definition of Done**
A story is Done when **all** of the following are true. Not "mostly true".
If one box is unticked, the story stays in the sprint and carries over.

| #   | Criterion                                                       | Who checks        |
| --- | --------------------------------------------------------------- | ----------------- |
| 1   | Every acceptance criterion on the issue passes                  | Reviewer, by hand |
| 2   | The feature works from a clean clone with only the README steps | Reviewer          |
| 3   | At least one automated test covers the new behaviour            | CI                |
| 4   | CI is green on the PR branch                                    | CI                |
| 5   | Code reviewed and approved by a teammate who did not write it   | GitHub            |
| 6   | Merged into `main`                                              | GitHub            |
| 7   | No secrets, `.env`, or database dumps in the diff               | CI                |
| 8   | `docs/traceability.md` updated if a screen or route changed     | Reviewer          |

## Run the walking skeleton

Requires Python 3.12 or newer. From the repository root, create and activate a
virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create the SQLite database and seed 12 courts with one command, then start the
web app:

```powershell
python init_db.py
python app.py
```

Open [http://127.0.0.1:5000/courts](http://127.0.0.1:5000/courts). See
[docs/SETUP.md](docs/SETUP.md) for configuration and test instructions.
