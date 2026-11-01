# 🐾 PawPal+

PawPal+ is a pet care planner built with Python and Streamlit. An owner enters how much time they have, adds their pets and each pet's care tasks (walks, feedings, meds, grooming, and so on), and PawPal+ builds a daily schedule that fits the most important tasks into that time, explains why each task was picked, and warns about overlapping times.

The logic lives in `pawpal_system.py` and was built and verified "CLI-first" with `main.py` and `pytest` before being connected to the Streamlit UI in `app.py`.

## ✨ Features

- **Owners with multiple pets:** each pet keeps its own task list, and the scheduler plans across all of them.
- **Priority-based planning:** tasks are chosen high → medium → low priority until the owner's available minutes run out. Tasks that don't fit are listed as skipped, not silently dropped.
- **Fixed and flexible times:** tasks with a preferred time are placed exactly there. Flexible tasks fill the earliest open gap from the start of the owner's day.
- **Sorting by time:** task lists are shown in chronological order, with flexible tasks last.
- **Filtering:** view tasks for one pet, by status (to do / done), or both.
- **Daily and weekly recurrence:** marking a recurring task done automatically creates its next occurrence (tomorrow, or in 7 days). One-off tasks just stay done.
- **Conflict warnings:** any two planned tasks whose time ranges overlap (including exact same start times) produce a readable warning instead of an error.
- **Explained plans:** every scheduled task comes with a short reason, such as "high priority, scheduled at its preferred time".

## 🚀 Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run the CLI demo:

```bash
python main.py
```

## 📁 Project structure

| File | Purpose |
|------|---------|
| `pawpal_system.py` | Logic layer: `Task`, `Pet`, `Owner`, and `Scheduler` |
| `app.py` | Streamlit UI that uses the logic layer |
| `main.py` | CLI demo script |
| `tests/test_pawpal.py` | Automated tests (pytest) |
| `diagrams/uml_draft.mmd` | Initial UML class diagram (Phase 1) |
| `diagrams/uml_final.mmd` | Final UML class diagram matching the code |
| `reflection.md` | Design and AI-collaboration reflection |

## 📐 Architecture

The final class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd). An `Owner` has one or more `Pet`s, each `Pet` has zero or more `Task`s, and the `Scheduler` reads the owner's pets and tasks to build a plan. When a recurring task is completed, the `Scheduler` asks the `Task` for its next occurrence and adds it back to the `Pet`.

## 🖥️ Sample Output

Output of `python main.py`:

```
All tasks, in the order they were added:
  08:00     Mochi  Morning walk   (daily, due 2026-11-01)
  flexible  Mochi  Bath           (weekly, due 2026-11-01)
  07:30     Mochi  Breakfast      (daily, due 2026-11-01)
  18:00     Luna   Dinner         (daily, due 2026-11-01)
  flexible  Luna   Brush coat     (daily, due 2026-11-01)
  07:30     Luna   Thyroid meds   (daily, due 2026-11-01)

Sorted by time:
  07:30     Mochi  Breakfast      (daily, due 2026-11-01)
  07:30     Luna   Thyroid meds   (daily, due 2026-11-01)
  08:00     Mochi  Morning walk   (daily, due 2026-11-01)
  18:00     Luna   Dinner         (daily, due 2026-11-01)
  flexible  Mochi  Bath           (weekly, due 2026-11-01)
  flexible  Luna   Brush coat     (daily, due 2026-11-01)

Only Luna's tasks:
  18:00     Luna   Dinner         (daily, due 2026-11-01)
  flexible  Luna   Brush coat     (daily, due 2026-11-01)
  07:30     Luna   Thyroid meds   (daily, due 2026-11-01)

Marked Mochi's Morning walk complete. Next one is due 2026-11-02.

Completed tasks:
  08:00     Mochi  Morning walk   (daily, done)

Mochi's tasks still to do:
  flexible  Mochi  Bath           (weekly, due 2026-11-01)
  07:30     Mochi  Breakfast      (daily, due 2026-11-01)
  08:00     Mochi  Morning walk   (daily, due 2026-11-02)

Today's Schedule for Jordan (85 of 90 min used)
------------------------------------------------------------
  07:00-07:15  Luna     Brush coat         (15 min)
               why: low priority, placed in the first open slot
  07:30-07:35  Luna     Thyroid meds       (5 min)
               why: high priority, scheduled at its preferred time
  07:30-07:40  Mochi    Breakfast          (10 min)
               why: medium priority, scheduled at its preferred time
  07:40-08:25  Mochi    Bath               (45 min)
               why: low priority, placed in the first open slot
  18:00-18:10  Luna     Dinner             (10 min)
               why: medium priority, scheduled at its preferred time

Conflicts:
  WARNING: Luna's Thyroid meds (07:30-07:35) overlaps Mochi's Breakfast (07:30-07:40)
```

## 🧪 Testing PawPal+

Run the full test suite from the project folder:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover:

- **Sorting:** `sort_by_time()` returns tasks in chronological order with flexible tasks last, `sort_tasks()` orders by priority, and the final plan comes out in time order.
- **Recurring tasks:** completing a daily task creates a new one due tomorrow, a weekly task repeats in 7 days, and a "once" task doesn't repeat. Completed tasks drop out of today's plan, and overdue tasks are still scheduled.
- **Conflict detection:** two tasks at the exact same time are flagged, overlapping durations are flagged, and back-to-back tasks (08:00–08:30, then 08:30) are not.
- **Filtering and time budget:** filtering by pet and/or completion status works. A task that doesn't fit is skipped while smaller tasks still fit, and 0 available minutes gives an empty plan.
- **Edge cases:** an owner with no pets, a pet with no tasks, flexible tasks filling gaps around fixed tasks, and two identical tasks counted separately.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Documents AP\FAU\CEN4010\CodePath\Week_4\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 21 items

tests\test_pawpal.py .....................                               [100%]

============================= 21 passed in 0.06s ==============================
```

**Confidence Level:** ★★★★☆ (4/5)

All 21 tests pass and cover the main scheduling behaviors and edge cases. I'm not giving it 5 stars because the Streamlit UI isn't covered by automated tests, invalid input (like a misspelled priority or a badly formatted time) isn't validated, and schedules that run past midnight aren't handled.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time()` | Sorts tasks by `preferred_time` using a `lambda` key on the "HH:MM" string. Zero-padded times sort correctly as text. Flexible tasks (no time) go last. |
| Sort by priority | `Scheduler.sort_tasks()`, `Task.priority_rank()` | Used when building the plan: high → medium → low, then earlier preferred time, then shorter duration. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Returns the owner's `(pet, task)` pairs for one pet, one completion status, or both. |
| Time budget | `Scheduler.fit_to_budget()` | Greedy: keeps tasks in priority order while they fit in `available_minutes`, and skips (but reports) the rest. |
| Placement | `Scheduler.generate_plan()`, `Scheduler._first_open_slot()` | Fixed-time tasks go at their preferred time. Flexible tasks fill the earliest open gap from `day_start`. |
| Conflict handling | `Scheduler.detect_conflicts()` | Checks every pair of planned tasks for overlapping time ranges (not just exact matches) and returns warning strings instead of raising. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()`, `Task.is_due()` | Completing a daily or weekly task adds a new copy due `today + timedelta(days=1 or 7)`. "once" tasks don't repeat. Only incomplete tasks due today or earlier are scheduled. |

## 📸 Demo Walkthrough

### Main UI features

- **Owner:** set the owner's name, minutes available today, and when the day starts.
- **Pets:** add a pet with a name, species, and age. Blank and duplicate names are rejected. A table shows each pet and how many tasks it has.
- **Add a task:** pick the pet, then enter the title, category, frequency (daily / weekly / once), duration, priority, and an optional preferred time.
- **Task list:** filter by pet and by status (To do / Done / All). The list is sorted by preferred time. Each due task has a **Done** button, future tasks show their due date, and every task has a **Remove** button.
- **Build Schedule:** **Generate schedule** shows today's plan as a table with start, end, pet, task, priority, and the reason it was chosen, plus any conflict warnings, a note about tasks that didn't fit, and a plain-text explanation.

### Example workflow

1. Open the app with `streamlit run app.py`. Set the owner to Jordan with 90 minutes available, starting at 07:00.
2. Add two pets: **Mochi** (dog) and **Luna** (cat).
3. Add tasks for Mochi: *Morning walk* (30 min, high, 08:00), *Breakfast* (10 min, medium, 07:30), and *Bath* (45 min, low, weekly, flexible).
4. Add tasks for Luna: *Thyroid meds* (5 min, high, 07:30), *Brush coat* (15 min, low, flexible), and *Dinner* (10 min, medium, 18:00).
5. Look at the task list. It's sorted by time (07:30, 07:30, 08:00, 18:00, then the flexible tasks). Set **Show pet** to Luna to see only Luna's tasks.
6. Click **Done** on Mochi's Morning walk. A success message says the next walk is due tomorrow, and the new walk appears in the list with that due date.
7. Click **Generate schedule**. The walk is no longer in today's plan, so the freed-up time lets the Bath fit. Flexible tasks are placed in open gaps (Brush coat at 07:00, Bath at 07:40).
8. A warning appears above the plan: *Luna's Thyroid meds (07:30-07:35) overlaps Mochi's Breakfast (07:30-07:40). Consider moving one of these tasks to a different time.*

### Key Scheduler behaviors shown

- **Sorting:** `sort_by_time()` orders the task list, and the plan comes out in time order.
- **Filtering:** `filter_tasks()` drives the pet and status dropdowns.
- **Recurrence:** `mark_task_complete()` creates the next daily or weekly occurrence.
- **Time budget:** `fit_to_budget()` drops lower-priority tasks first when time runs out.
- **Conflict warnings:** `detect_conflicts()` flags the overlapping 07:30 tasks.

### Sample CLI output

The same scenario run through `python main.py`. The full output, including the sorting, filtering, and recurrence steps, is in the Sample Output section above.

```
Today's Schedule for Jordan (85 of 90 min used)
------------------------------------------------------------
  07:00-07:15  Luna     Brush coat         (15 min)
               why: low priority, placed in the first open slot
  07:30-07:35  Luna     Thyroid meds       (5 min)
               why: high priority, scheduled at its preferred time
  07:30-07:40  Mochi    Breakfast          (10 min)
               why: medium priority, scheduled at its preferred time
  07:40-08:25  Mochi    Bath               (45 min)
               why: low priority, placed in the first open slot
  18:00-18:10  Luna     Dinner             (10 min)
               why: medium priority, scheduled at its preferred time

Conflicts:
  WARNING: Luna's Thyroid meds (07:30-07:35) overlaps Mochi's Breakfast (07:30-07:40)
```
