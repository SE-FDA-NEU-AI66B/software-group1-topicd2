# Sprint log

One section per sprint. Fill it in **during** the sprint, not the night before
the milestone deadline - the commit timestamps on this file are part of the
evidence that the process was real.

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

**Total committed: 17 Points**

### Result

| Issue | Est. hours | Status | If not done, why                               |
| ----- | ---------- | ------ | ---------------------------------------------- |
| #86   | 1          | Done   | Closed; linked PR #97 merged                   |
| #87   | 1          | Done   | Closed; linked PR #97 merged                   |
| #88   | 1          | Done   | Closed; backlog acceptance checklist completed |
| #89   | 1          | Done   | Closed; sprint acceptance checklist completed  |
| #90   | 1          | Done   | Closed; linked PR #98 merged                   |
| #91   | 3          | Done   | Closed; linked PR #99 merged                   |
| #92   | 3          | Done   | Closed; linked PR #100 merged                  |
| #93   | 2          | Done   | Closed; linked PR #101 merged                  |
| #94   | 2          | Done   | Closed; linked PR #102 merged                  |
| #95   | 2          | Done   | Closed; linked PR #103 merged                  |
| #96   | 2          | Done   | Closed; linked PR #104 merged                  |

- **Goal**: Deliver the P0 SmashGo experience from court discovery through booking and payment, including authentication, booking management, Admin court controls, and aligned UI documentation.
- **Committed**: 17 points
- **Completed**: 17 points (11 of 11 issues)
- **Velocity**: not applicable
- **Not finished**: 0
- **SM Sprint 3**: @dqchien

**Completed: 18 of 19 estimated hours. Velocity this sprint: not applicable**

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
