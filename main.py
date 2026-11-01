"""CLI demo for PawPal+: builds a sample owner with two pets and exercises the scheduler."""

from datetime import date

from pawpal_system import Owner, Pet, PetTask, Scheduler, Task


def print_tasks(heading: str, tasks: list[PetTask]) -> None:
    """Print a short list of (pet, task) pairs under a heading."""
    print(heading)
    for pet, task in tasks:
        time = task.preferred_time or "flexible"
        status = "done" if task.completed else f"due {task.due_date}"
        print(f"  {time:<9} {pet.name:<6} {task.title:<14} ({task.frequency}, {status})")
    print()


def main() -> None:
    today = date.today()
    owner = Owner(name="Jordan", available_minutes=90, day_start="07:00")

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of time order on purpose so sort_by_time() has something to fix.
    luna.add_task(Task("Dinner", 10, "medium", category="feeding", preferred_time="18:00"))
    mochi.add_task(Task("Morning walk", 30, "high", category="walk", preferred_time="08:00"))
    luna.add_task(Task("Brush coat", 15, "low", category="grooming"))
    mochi.add_task(Task("Bath", 45, "low", category="grooming", frequency="weekly"))
    luna.add_task(Task("Thyroid meds", 5, "high", category="meds", preferred_time="07:30"))
    # Same time as Luna's meds, to show conflict detection.
    mochi.add_task(Task("Breakfast", 10, "medium", category="feeding", preferred_time="07:30"))

    scheduler = Scheduler(owner)

    print_tasks("All tasks, in the order they were added:", owner.get_all_tasks())
    print_tasks("Sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
    print_tasks("Only Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))

    walk = next(t for t in mochi.tasks if t.title == "Morning walk")
    next_walk = scheduler.mark_task_complete(mochi, walk, today)
    print(f"Marked Mochi's Morning walk complete. Next one is due {next_walk.due_date}.\n")
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks("Mochi's tasks still to do:", scheduler.filter_tasks(pet_name="Mochi", completed=False))

    plan = scheduler.generate_plan(today)
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
