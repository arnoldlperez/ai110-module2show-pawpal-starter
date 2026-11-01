"""CLI demo for PawPal+: builds a sample owner with two pets and prints today's schedule."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90, day_start="07:00")

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", category="walk", preferred_time="08:00"))
    mochi.add_task(Task("Breakfast", 10, "medium", category="feeding"))
    mochi.add_task(Task("Bath", 45, "low", category="grooming", frequency="weekly"))
    luna.add_task(Task("Thyroid meds", 5, "high", category="meds", preferred_time="07:30"))
    luna.add_task(Task("Brush coat", 15, "low", category="grooming"))
    luna.add_task(Task("Dinner", 10, "medium", category="feeding", preferred_time="18:00"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(date.today())
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
