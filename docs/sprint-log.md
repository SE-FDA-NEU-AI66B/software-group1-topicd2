# Sprint log

One section per sprint. Fill it in **during** the sprint, not the night before
the milestone deadline - the commit timestamps on this file are part of the
evidence that the process was real.

---

## Sprint summary

The unit follows the estimate recorded for each sprint: Sprint 1 uses story
points; Sprints 3-5 use estimated hours. Sprint 2 results were not recorded in
this file and have not been reconstructed.

| Sprint | Committed | Completed | Velocity |
| ------ | --------- | --------- | -------- |
| Sprint 1 | 30 points | 30 points | Not applicable (as recorded) |
| Sprint 2 | Not recorded | Not recorded | Not recorded |
| Sprint 3 | 19 hours | 19 hours | 19 hours |
| Sprint 4 | 14 hours | 14 hours | 14 hours |
| Sprint 5 | 12 hours | 11 hours (6/7 issues; #131 pending merge) | 11 hours so far |

Sprint 5 velocity is provisional until the wrap-up PR is merged. Sprint 2's
missing figures need the original planning record before they can be filled in.

---

## Sprint 1 - 10 Sep 2026 to 22 Sep 2026

<!-- Sprint 1: weeks 5-6 | Sprint 2: 7-8 | Sprint 3: 9-10 | Sprint 4: 11-12 | Sprint 5: 13-14 -->

### Sprint goal

Build the core booking foundation for SmashGo, including defining user stories, acceptance criteria, and the basic booking flow.

### Mandatory Chore Issues

| Issue                                   | Assignee              | Closed? |
| --------------------------------------- | --------------------- | ------- |
| [Chore] Refine backlog for Sprint 1 #13 | @dqchien (PO)         | Yes     |
| [Chore] Sprint 1 wrap-up #16            | @quynhquynh-blip (SM) | Yes     |

### Committed

| Issue | Story                                                            | Points | Owner                                     |
| ----- | ---------------------------------------------------------------- | ------ | ----------------------------------------- |
| #11   | [Task] Product Vision & Personas (2 personas + interviews)       | 3      | @dqchien                                  |
| #12   | [Task] Business Rules (BR1–BR6)                                  | 3      | @dqchien                                  |
| #13   | [Chore] Refine backlog for Sprint 1                              | 3      | @dqchien                                  |
| #14   | [Task] Scenarios (2 use scenarios)                               | 3      | @quynhquynh-blip                          |
| #15   | [Task] Screens & Flow Diagram                                    | 3      | @quynhquynh-blip                          |
| #16   | [Chore] Sprint 1 wrap-up                                         | 3      | @quynhquynh-blip                          |
| #17   | [Task] 10 User Stories + Acceptance Criteria                     | 3      | @Buithaoaineu                             |
| #18   | [Repo] Create 10 GitHub issues labeled "story" + assign Sprint 1 | 3      | @Buithaoaineu                             |
| #19   | [Task] README + docs/sprint-log.md                               | 3      | @Buithaoaineu                             |
| #20   | [Shared] Merge files, peer review, export PDF submission         | 3      | @quynhquynh-blip, @Buithaoaineu, @dqchien |

**Total committed: 30 points**

### Result

| Issue | Points | Status | If not done, why |
| ----- | ------ | ------ | ---------------- |
| #11   | 3      | Done   | Completed        |
| #12   | 3      | Done   | Completed        |
| #13   | 3      | Done   | Completed        |
| #14   | 3      | Done   | Completed        |
| #15   | 3      | Done   | Completed        |
| #16   | 3      | Done   | Completed        |
| #17   | 3      | Done   | Completed        |
| #18   | 3      | Done   | Completed        |
| #19   | 3      | Done   | Completed        |
| #20   | 3      | Done   | Completed        |

- **Goal**: Build the core booking foundation for SmashGo, including defining user stories, acceptance criteria, and the basic booking flow.
- **Committed**: 30 points
- **Completed**: 30 points
- **Velocity**: not applicable
- **Not finished**: None
- **SM Sprint 2**: @Buithaoaineu

**Completed: 30 points. Velocity this sprint: not applicable**

### Sprint Review

- What we demonstrated: Product Vision, 2 Personas, Business Rules (BR1-BR6), 10 User Stories with Acceptance Criteria, 2 Scenarios, UI Screens & Flow Diagram, and finalized assignment document.
- Feedback received: The core booking flow and functional requirements are well-defined, clear, and ready for technical implementation.
- Backlog changes as a result: Decompose the high-priority User Stories into technical architecture and implementation tasks for Sprint 2.

### Retrospective

| Keep doing                                                   | Stop doing                                                             | Start doing                                                         |
| ------------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Maintaining clear task delegation and effective cross-review | Merging documentation and finalizing exports right before the deadline | Estimating Story Points using Planning Poker starting from Sprint 2 |
| Keeping GitHub Project boards and branch naming standardized | Delaying reviews on open pull requests                                 | Defining automated testing criteria along with development tasks    |

**One concrete action for next sprint (with an owner):**

- Set up the database schema and initialize core booking API endpoints (Owner: @dqchien).

<!-- A retro that produces no action item is a complaint session.
     Exactly one action, one owner, checked at the next retro. -->

### Attendance

| Member           | Planning | Review | Retro |
| ---------------- | -------- | ------ | ----- |
| @quynhquynh-blip | Yes      | Yes    | Yes   |
| @dqchien         | Yes      | Yes    | Yes   |
| @Buithaoaineu    | Yes      | Yes    | Yes   |

---

## Sprint 3 - 12 Oct 2026 to 20 Oct 2026

### Sprint goal

Deliver the P0 SmashGo experience from court discovery through booking and payment, including authentication, booking management, and Admin court controls; align the UI and design documentation with the delivered flows.

### Mandatory Chore Issues

| Issue                                   | Assignee      | Closed? |
| --------------------------------------- | ------------- | ------- |
| [Chore] Refine backlog for Sprint 3 #88 | @dqchien (PO) | Yes     |
| [Chore] Sprint 3 wrap-up #89            | @dqchien (SM) | Yes\*   |

### Committed

| Issue | Story                                                           | Est. hours | Owner            |
| ----- | --------------------------------------------------------------- | ---------- | ---------------- |
| #86   | [Fix] Resolve conflicts in docs/design.md (M2)                  | 1          | @dqchien         |
| #87   | [Fix] Resolve conflicts in docs/requirements.md (M1)            | 1          | @dqchien         |
| #88   | [Chore] Refine backlog for Sprint 3                             | 1          | @dqchien         |
| #89   | [Chore] Sprint 3 wrap-up                                        | 1          | @dqchien         |
| #90   | [UI] Login/Register, shared UI, and seed data                   | 2          | @dqchien         |
| #91   | [UI] /book: slot selection, hold, and double-booking prevention | 3          | @quynhquynh-blip |
| #92   | [UI] /book: bank linking, OTP, and payment                      | 3          | @quynhquynh-blip |
| #93   | [UI] /my-bookings: view and cancel bookings                     | 1          | @quynhquynh-blip |
| #94   | [UI] /admin/courts: review requests and enable/disable courts   | 2          | @Buithaoaineu    |
| #95   | [UI] Court discovery and /availability                          | 2          | @Buithaoaineu    |
| #96   | [Docs] Write docs/ui.md                                         | 2          | @Buithaoaineu    |

**Total committed: 19 estimated hours**

### Result

| Issue | Est. hours | Status | If not done, why                               |
| ----- | ---------- | ------ | ---------------------------------------------- |
| #86   | 1          | Done   | Closed; linked PR #97 merged                   |
| #87   | 1          | Done   | Closed; linked PR #97 merged                   |
| #88   | 1          | Done   | Closed; backlog acceptance checklist completed |
| #89   | 1          | Done   | Closed; sprint acceptance checklist completed  |
| #90   | 2          | Done   | Closed; linked PR #98 merged                   |
| #91   | 3          | Done   | Closed; linked PR #99 merged                   |
| #92   | 3          | Done   | Closed; linked PR #100 merged                  |
| #93   | 1          | Done   | Closed; linked PR #101 merged                  |
| #94   | 2          | Done   | Closed; linked PR #102 merged                  |
| #95   | 2          | Done   | Closed; linked PR #103 merged                  |
| #96   | 2          | Done   | Closed; linked PR #104 merged                  |

- **Goal**: Deliver the P0 SmashGo experience from court discovery through booking and payment, including authentication, booking management, Admin court controls, and aligned UI documentation.
- **Committed**: 19 estimated hours
- **Completed**: 19 estimated hours (11 of 11 issues)
- **Velocity**: 19 estimated hours
- **Not finished**: 0
- **SM Sprint 3**: @dqchien

**Completed: 19 of 19 estimated hours. Velocity this sprint: 19 hours**

### Sprint Review

- What we demonstrated: Court discovery and availability, sign-in and registration, booking holds and payment, booking history and cancellation, Admin court review and status controls, and the corresponding UI flows documented in `docs/ui.md`.
- Feedback received: Not recorded in the repository.
- Backlog changes as a result: The Manager court workspace remains a placeholder; continue with the P1 Manager court-management stories.

### Retrospective

| Keep doing                                                                          | Stop doing                                                          | Start doing                                                            |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Assigning clear owners and merging reviewed work through issue-linked pull requests | Closing a wrap-up issue before its acceptance checklist is verified | Keep the sprint log and issue checklists current throughout the sprint |

**One concrete action for next sprint (with an owner):**

- Implement the P1 Manager court workspace for US-15 to US-17.

### Attendance

| Member           | Planning | Review | Retro |
| ---------------- | -------- | ------ | ----- |
| @quynhquynh-blip | Yes      | Yes    | Yes   |
| @dqchien         | Yes      | Yes    | Yes   |
| @Buithaoaineu    | Yes      | Yes    | Yes   |

---

## Sprint 4 - 29 Oct 2026 to the Milestone 4 deadline

### Sprint goal

Prove that the P0 stories work: give every P0 story (US-01 to US-05, US-11, US-12) traceable test cases with normal, error and boundary cases, make `pytest` pass on a clean clone without a server, a real database or the real date, and write `docs/testing.md` for Milestone 4.

### Mandatory Chore Issues

| Issue                                    | Assignee              | Closed? |
| ---------------------------------------- | --------------------- | ------- |
| [Chore] Refine backlog for Sprint 4 #113 | @dqchien (PO)         | Yes     |
| [Chore] Sprint 4 wrap-up #112            | @quynhquynh-blip (SM) | No      |

### Committed

| Issue | Story                                                                    | Est. hours | Owner            |
| ----- | ------------------------------------------------------------------------ | ---------- | ---------------- |
| #109  | [Task] pytest infrastructure: runs on a clean machine + SETUP.md         | 1          | @quynhquynh-blip |
| #110  | [Task] Test US-04/US-05: create booking (BR1, BR2, BR6, double booking)  | 2          | @Buithaoaineu    |
| #111  | [Task] Test US-04: 10-minute hold, bank linking, payment, OTP (BR3, BR7) | 2          | @Buithaoaineu    |
| #112  | [Chore] Sprint 4 wrap-up                                                 | 1          | @quynhquynh-blip |
| #113  | [Chore] Refine backlog for Sprint 4                                      | 1          | @dqchien         |
| #114  | [Task] Write docs/testing.md (4 sections) and export the M4 PDF          | 3          | @dqchien         |
| #115  | [Task] Test US-01, US-02, US-03: court list, court detail, free slots    | 2          | @quynhquynh-blip |
| #116  | [Task] Test US-11, US-12: Admin enables/disables courts, reviews requests | 2          | @dqchien         |

**Total committed: 14 points** (1 point = 1 estimated hour, as in Sprint 3)

### Result

Status on 15 Nov 2026. All Sprint 4 issues are closed.

| Issue | Est. hours | Status | If not done, why |
| ----- | ---------- | ------ | ---------------- |
| #109  | 1          | Done   | Closed; test fixtures and SETUP.md merged         |
| #110  | 2          | Done   | Closed; booking tests merged                      |
| #111  | 2          | Done   | Closed; payment and OTP tests merged              |
| #112  | 1          | Done   | Closed; Sprint 4 wrap-up merged                   |
| #113  | 1          | Done   | Closed; backlog and planning board ready          |
| #114  | 3          | Done   | Closed; linked PR #117 merged                     |
| #115  | 2          | Done   | Closed; court discovery tests merged              |
| #116  | 2          | Done   | Closed; Admin tests merged                        |

- **Goal**: Every P0 story has traceable tests (normal, error, boundary) that pass on a clean clone, documented in `docs/testing.md`.
- **Committed**: 14 points
- **Completed**: 14 estimated hours (8 of 8 issues)
- **Velocity**: 14 estimated hours
- **Not finished**: None
- **SM Sprint 4**: @quynhquynh-blip

### Repository checklist (Milestone 4)

Checked on 31 Oct 2026; tick the rest before the deadline.

- [ ] At least 4 PRs merged in Sprint 4, each reviewed by someone other than its author (1 so far: #117, reviewed by @quynhquynh-blip)
- [ ] At least 5 issues closed in Sprint 4 (2 so far: #113, #114)
- [ ] Every member has at least 1 merged PR in Sprint 4 (@dqchien: #117; @quynhquynh-blip and @Buithaoaineu: pending)
- [ ] Every member has done at least 1 review in Sprint 4 (@quynhquynh-blip: #117; @dqchien and @Buithaoaineu: pending)
- [ ] Every member has closed at least 1 issue in Sprint 4 (@dqchien: #113, #114; others pending)
- [x] Every member has at least 1 test in `tests/` (all three have commits in `tests/`)
- [x] `docs/SETUP.md` is on `main` (the test-run section arrives with #109)
- [ ] Board screenshot taken on the submission day (page 2 of the PDF)
- [ ] Every member cloned into a new folder and ran `pytest` before the deadline

### Sprint Review

- What we demonstrated: To be filled in at the Sprint Review.
- Feedback received: To be filled in at the Sprint Review.
- Backlog changes as a result: To be filled in at the Sprint Review.

### Retrospective

| Keep doing | Stop doing | Start doing |
| ---------- | ---------- | ----------- |
| To be filled in at the retro | | |

**One concrete action for next sprint (with an owner):**

- To be agreed at the retro.

### Attendance

| Member           | Planning | Review | Retro |
| ---------------- | -------- | ------ | ----- |
| @quynhquynh-blip |          |        |       |
| @dqchien         |          |        |       |
| @Buithaoaineu    |          |        |       |

---

## Sprint 5 - 7 Nov 2026 to the Milestone 5 deadline

### Sprint goal

Put SmashGo online at one public `https://` URL that a stranger can open on a phone or a laptop and use every P0 story (US-01 to US-05, US-11, US-12) by clicking only. A merge into `main` reaches the URL only after CI is green. `/health` reports the state of the app and the database, and `docs/operations.md` explains how we release, roll back, monitor and maintain the app. The version at the URL is tagged `v1.0` and shown at the final demo in week 15.

### Mandatory Chore Issues

| Issue                                   | Assignee            | Closed? |
| --------------------------------------- | ------------------- | ------- |
| [Chore] Refine backlog Sprint 5 #125    | @dqchien (PO)       | No      |
| [Chore] Sprint 5 wrap-up #131           | @Buithaoaineu (SM)  | No      |

### Planning board

![Sprint 5 planning board](../images/Sprint%205%20Planning.PNG)

### Committed

| Issue | Story                                                                        | Est. hours | Owner            |
| ----- | ---------------------------------------------------------------------------- | ---------- | ---------------- |
| #125  | [Chore] Refine backlog Sprint 5                                              | 1          | @dqchien         |
| #126  | [Task] Deploy the app to Render with gunicorn, deploy only when CI is green  | 2          | @dqchien         |
| #127  | [Task] Add the `/health` endpoint and request logging                        | 2          | @quynhquynh-blip |
| #128  | [Task] Apply the M3 feedback to the interface (before / after)               | 2          | @Buithaoaineu    |
| #129  | [Task] Write `docs/operations.md` (7 sections)                               | 2          | @quynhquynh-blip |
| #130  | [Task] Branch protection, CI badge and the README first screen               | 2          | @dqchien         |
| #131  | [Chore] Sprint 5 wrap-up                                                     | 1          | @Buithaoaineu    |

**Total committed: 12 points** (1 point = 1 estimated hour, as in Sprints 3 and 4)

Order of work: #126 (deploy) and #127 (`/health`) first, because #129 and #130 need the real URL, a CI run and the logs. The release `v1.0` and the final demo are done by the whole team without a pull request, so they are not on the board.

### M3 feedback to fix (input for #128)

| #  | Feedback from M3 | Screen | Priority | Fixed in |
| -- | ---------------- | ------ | -------- | -------- |
| 1 | The court checkbox cannot be ticked on a desktop browser | `/book` | Must | #128 |
| 2 | The end-time list goes to 23:00, but the time grid above only shows up to 22:00 | `/book` | Must | #128 |
| 3 | The price is written 90,000 on the court list and 90.000 inside; use one format everywhere | `/courts`, `/courts/{courtId}`, `/book` | Must | #128 |
| 4 | The payment page shows too many forms and buttons at once | `/book` (payment) | Must | #128 |
| 5 | Payment should be step by step: the next step appears only when the previous one is done | `/book` (payment) | Must | #128 |
| 6 | The *Court details* and *Book* buttons sit in the status column | `/courts` | Must | #128 |
| 7 | The text is too small | All screens | Must | #128 |
| 8 | The Admin screen shows the raw value `active` in English while the rest of the page is Vietnamese | `/admin/courts` | Must | #128 |
| 9 | The layout leaves too much empty space | All screens | Should | #128 if time allows |
| 10 | A user cannot select several time slots in one booking | `/book` | Later | Not in Sprint 5: US-04 books one slot; listed as a known risk in `docs/operations.md` |

Priority: **Must** = fixed in Sprint 5 (bugs and inconsistencies the demo will show before / after); **Should** = if time allows; **Later** = changes the scope of a P0 story, so it is not a UI fix.

### Result

Status on 15 Nov 2026. The Sprint 5 task issues are closed; this wrap-up issue
is pending review and closes when this change is merged.

| Issue | Est. hours | Status | If not done, why |
| ----- | ---------- | ------ | ---------------- |
| #125  | 1          | Done   | Closed; backlog and plan recorded in PR #132 |
| #126  | 2          | Done   | Closed; deployment and public URL documented in PRs #133, #137 |
| #127  | 2          | Done   | Closed; `/health` and request logging merged in PR #135 |
| #128  | 2          | Done   | Closed; M3 interface feedback fixed in PR #139 |
| #129  | 2          | Done   | Closed; operations guide merged in PR #136 |
| #130  | 2          | Done   | Closed; branch protection and README update merged in PR #138 |
| #131  | 1          | In progress | This wrap-up; closes when this change is merged |

- **Goal**: One public URL running `v1.0`, deployed from `main` only after CI is green, with `/health` and `docs/operations.md`.
- **Committed**: 12 points
- **Completed**: 11 of 12 estimated hours (6 of 7 issues; #131 is this wrap-up)
- **Velocity**: 11 estimated hours so far; recompute after #131 merges
- **Not finished**: #131, pending review and merge
- **SM Sprint 5**: @Buithaoaineu

### Repository checklist (Sprint 5)

Checked on 15 Nov 2026. These seven merged PRs each had passing status checks
and an approval from another team member:

| PR | Author | Reviewer | Checks |
| -- | ------ | -------- | ------ |
| #132 | @dqchien | @quynhquynh-blip | Passed |
| #133 | @dqchien | @quynhquynh-blip | Passed |
| #135 | @quynhquynh-blip | @Buithaoaineu | Passed |
| #136 | @quynhquynh-blip | @Buithaoaineu | Passed |
| #137 | @dqchien | @quynhquynh-blip | Passed |
| #138 | @dqchien | @quynhquynh-blip | Passed |
| #139 | @Buithaoaineu | @dqchien | Passed |

PR #134 was also merged, but is not counted: it was an unrelated cleanup and
its recorded checks include a failure.

| Requirement | Evidence |
| ----------- | -------- |
| At least 4 merged PRs with green checks and another member's review | #132, #133, #135, #136, #137, #138, #139 |
| Every member has at least 1 merged PR | @dqchien: #132; @quynhquynh-blip: #135; @Buithaoaineu: #139 |
| Every member has completed at least 1 review | @dqchien: #139; @quynhquynh-blip: #132; @Buithaoaineu: #135 |
| Every member has at least 1 closed issue | @dqchien: #125; @quynhquynh-blip: #127; @Buithaoaineu: #128 |

The public URL, `/health` and operations guide are recorded. The `v1.0` tag and
final demo were not found in the repository as of 15 Nov 2026; confirm these
before declaring the Sprint 5 goal fully met.

### Sprint Review

- What we demonstrated: the public SmashGo URL, `/health`, deployment after green CI, the operations guide, and the M3 interface fixes.
- Feedback received: No additional Sprint 5 review feedback is recorded in the repository.
- Backlog changes as a result: Keep multi-slot booking out of scope as recorded in `docs/operations.md`; continue the deferred P1 Manager stories.

### Retrospective

These observations are based on the repository record; confirm them with the
team at the retrospective.

| Keep doing | Stop doing | Start doing |
| ---------- | ---------- | ----------- |
| Peer review and green CI before merging, as shown by the qualifying Sprint 5 PRs | Leaving sprint result fields blank until wrap-up | Update the sprint log and release evidence as issues close |

**One concrete action for next sprint (with an owner):**

- Update the sprint log and release evidence during the sprint as work closes (Owner: @Buithaoaineu).
