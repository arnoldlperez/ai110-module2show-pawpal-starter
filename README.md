# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
