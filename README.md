# Sports Booking Platform

Sports field booking platform for players, helping to find a field, choose a time slot and book quickly, while avoiding double bookings and sending reminders before the game schedule.

**Group:** 1

**Topic:** D2

**Member:**

- Chu Vu Thao Hien - @dqchien
- Phan Thi Anh Quynh - @quynhquynh-blip
- Bui Phuong Thao - @Buithaoaineu

**Product Owner (fixed for the whole period):** @dqchien

**Scrum Master (rotating every sprint):** @quynhquynh-blip (Sprint 1)

**Board:** https://github.com/orgs/SE-FDA-NEU-AI66B/projects/24

**Definition of Done** 
A story is Done when **all** of the following are true. Not "mostly true".
If one box is unticked, the story stays in the sprint and carries over.

| # | Criterion | Who checks |
|---|-----------|------------|
| 1 | Every acceptance criterion on the issue passes | Reviewer, by hand |
| 2 | The feature works from a clean clone with only the README steps | Reviewer |
| 3 | At least one automated test covers the new behaviour | CI |
| 4 | CI is green on the PR branch | CI |
| 5 | Code reviewed and approved by a teammate who did not write it | GitHub |
| 6 | Merged into `main` | GitHub |
| 7 | No secrets, `.env`, or database dumps in the diff | CI |
| 8 | `docs/traceability.md` updated if a screen or route changed | Reviewer |

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
