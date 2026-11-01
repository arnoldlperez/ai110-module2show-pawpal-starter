from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 11, 1)


def make_task(title, duration=10, priority="medium", time=None, frequency="daily", due=TODAY):
    """Build a Task with a fixed due date so tests don't depend on the real date."""
    return Task(title, duration, priority, preferred_time=time, frequency=frequency, due_date=due)


def make_scheduler(available=120, day_start="07:00", **pets):
    """Build a Scheduler for an owner whose pets are given as name=[tasks]."""
    owner = Owner("Jordan", available_minutes=available, day_start=day_start)
    for name, tasks in pets.items():
        pet = Pet(name, "dog")
        for task in tasks:
            pet.add_task(task)
        owner.add_pet(pet)
    return Scheduler(owner)


def titles(items):
    """Return task titles from (pet, task) pairs or plan items."""
    return [item[2].title if len(item) == 4 else item[1].title for item in items]


# --- Basic Task and Pet behavior ---

def test_mark_complete_changes_status():
    task = make_task("Morning walk")
    assert not task.completed
    assert task.is_due(TODAY)

    task.mark_complete()

    assert task.completed
    assert not task.is_due(TODAY)


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task("Breakfast"))

    assert len(pet.get_tasks()) == 1


def test_time_helpers_round_trip():
    assert Scheduler.to_minutes("08:30") == 510
    assert Scheduler.to_hhmm(510) == "08:30"
    assert Scheduler.to_hhmm(Scheduler.to_minutes("00:05")) == "00:05"


# --- Sorting ---

def test_sort_by_time_returns_chronological_order_with_flexible_last():
    scheduler = make_scheduler(
        Mochi=[make_task("Dinner", time="18:00"), make_task("Brush"), make_task("Walk", time="08:00")],
        Luna=[make_task("Meds", time="07:30")],
    )

    result = scheduler.sort_by_time(scheduler.owner.get_all_tasks())

    assert titles(result) == ["Meds", "Walk", "Dinner", "Brush"]


def test_sort_tasks_orders_by_priority_first():
    scheduler = make_scheduler(
        Mochi=[make_task("Low", priority="low"), make_task("High", priority="high"), make_task("Mid")],
    )

    result = scheduler.sort_tasks(scheduler.owner.get_all_tasks())

    assert titles(result) == ["High", "Mid", "Low"]


def test_plan_is_in_chronological_order():
    scheduler = make_scheduler(
        Mochi=[make_task("Dinner", time="18:00"), make_task("Walk", time="08:00"), make_task("Brush")],
    )

    plan = scheduler.generate_plan(TODAY)

    starts = [Scheduler.to_minutes(start) for start, _, _, _ in plan]
    assert starts == sorted(starts)


# --- Recurrence ---

def test_completing_daily_task_creates_one_for_tomorrow():
    walk = make_task("Walk", frequency="daily")
    scheduler = make_scheduler(Mochi=[walk])
    mochi = scheduler.owner.pets[0]

    next_walk = scheduler.mark_task_complete(mochi, walk, TODAY)

    assert walk.completed
    assert next_walk is not None
    assert next_walk.due_date == TODAY + timedelta(days=1)
    assert not next_walk.completed
    assert next_walk.title == "Walk"
    assert len(mochi.tasks) == 2


def test_completing_weekly_task_creates_one_for_next_week():
    bath = make_task("Bath", frequency="weekly")
    scheduler = make_scheduler(Mochi=[bath])

    next_bath = scheduler.mark_task_complete(scheduler.owner.pets[0], bath, TODAY)

    assert next_bath.due_date == TODAY + timedelta(days=7)


def test_completing_one_off_task_does_not_repeat():
    vet = make_task("Vet visit", frequency="once")
    scheduler = make_scheduler(Mochi=[vet])

    result = scheduler.mark_task_complete(scheduler.owner.pets[0], vet, TODAY)

    assert result is None
    assert len(scheduler.owner.pets[0].tasks) == 1


def test_completed_task_and_its_next_occurrence_are_not_in_todays_plan():
    walk = make_task("Walk")
    scheduler = make_scheduler(Mochi=[walk, make_task("Breakfast")])
    scheduler.mark_task_complete(scheduler.owner.pets[0], walk, TODAY)

    plan = scheduler.generate_plan(TODAY)

    assert titles(plan) == ["Breakfast"]
    # The new walk shows up the next day.
    assert "Walk" in titles(scheduler.generate_plan(TODAY + timedelta(days=1)))


def test_overdue_task_is_still_scheduled():
    scheduler = make_scheduler(Mochi=[make_task("Meds", due=TODAY - timedelta(days=2))])

    assert titles(scheduler.generate_plan(TODAY)) == ["Meds"]


# --- Conflict detection ---

def test_detects_two_tasks_at_the_same_time():
    scheduler = make_scheduler(
        Mochi=[make_task("Breakfast", time="07:30")],
        Luna=[make_task("Meds", time="07:30")],
    )

    conflicts = scheduler.detect_conflicts(scheduler.generate_plan(TODAY))

    assert len(conflicts) == 1
    assert "Breakfast" in conflicts[0] and "Meds" in conflicts[0]


def test_detects_overlapping_durations():
    scheduler = make_scheduler(
        Mochi=[make_task("Walk", duration=30, time="08:00"), make_task("Meds", duration=5, time="08:15")],
    )

    assert len(scheduler.detect_conflicts(scheduler.generate_plan(TODAY))) == 1


def test_back_to_back_tasks_are_not_a_conflict():
    scheduler = make_scheduler(
        Mochi=[make_task("Walk", duration=30, time="08:00"), make_task("Breakfast", time="08:30")],
    )

    assert scheduler.detect_conflicts(scheduler.generate_plan(TODAY)) == []


def test_flexible_tasks_fill_gaps_without_conflicts():
    scheduler = make_scheduler(
        day_start="07:00",
        Mochi=[make_task("Walk", duration=30, time="07:15"), make_task("Brush", duration=20)],
    )

    plan = scheduler.generate_plan(TODAY)

    brush_start = next(start for start, _, task, _ in plan if task.title == "Brush")
    # 07:00-07:15 is too short for a 20 minute task, so it goes right after the walk.
    assert brush_start == "07:45"
    assert scheduler.detect_conflicts(plan) == []


# --- Filtering and time budget ---

def test_filter_by_pet_and_status():
    scheduler = make_scheduler(Mochi=[make_task("Walk"), make_task("Breakfast")], Luna=[make_task("Meds")])
    walk = scheduler.owner.pets[0].tasks[0]
    walk.mark_complete()

    assert titles(scheduler.filter_tasks(pet_name="Luna")) == ["Meds"]
    assert titles(scheduler.filter_tasks(completed=True)) == ["Walk"]
    assert titles(scheduler.filter_tasks(pet_name="Mochi", completed=False)) == ["Breakfast"]
    assert scheduler.filter_tasks(pet_name="Nobody") == []


def test_task_that_does_not_fit_is_skipped_but_smaller_ones_still_fit():
    scheduler = make_scheduler(
        available=60,
        Mochi=[
            make_task("Walk", duration=30, priority="high"),
            make_task("Bath", duration=45, priority="medium"),
            make_task("Brush", duration=15, priority="low"),
        ],
    )

    plan = scheduler.generate_plan(TODAY)

    assert sorted(titles(plan)) == ["Brush", "Walk"]
    assert titles(scheduler.skipped) == ["Bath"]


def test_zero_available_minutes_gives_empty_plan():
    scheduler = make_scheduler(available=0, Mochi=[make_task("Walk")])

    assert scheduler.generate_plan(TODAY) == []
    assert titles(scheduler.skipped) == ["Walk"]


def test_identical_tasks_are_both_counted():
    scheduler = make_scheduler(available=10, Mochi=[make_task("Treat", duration=10), make_task("Treat", duration=10)])

    plan = scheduler.generate_plan(TODAY)

    assert len(plan) == 1
    assert len(scheduler.skipped) == 1


# --- Empty cases ---

def test_owner_with_no_pets_gets_empty_plan():
    scheduler = make_scheduler()

    plan = scheduler.generate_plan(TODAY)

    assert plan == []
    assert "No tasks scheduled" in scheduler.explain_plan(plan)


def test_pet_with_no_tasks_gets_empty_plan():
    scheduler = make_scheduler(Mochi=[])

    assert scheduler.generate_plan(TODAY) == []
    assert scheduler.detect_conflicts([]) == []
