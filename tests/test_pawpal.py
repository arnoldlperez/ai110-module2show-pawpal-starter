from datetime import date

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    today = date(2026, 11, 1)
    task = Task("Morning walk", 30, "high", due_date=today)
    assert not task.completed
    assert task.is_due(today)

    task.mark_complete()

    assert task.completed
    assert not task.is_due(today)


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Breakfast", 10, "medium"))

    assert len(pet.get_tasks()) == 1
