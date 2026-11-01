"""PawPal+ logic layer: classes for owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task, like a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str = "other"  # e.g. "walk", "feeding", "meds", "grooming"
    preferred_time: str | None = None  # "HH:MM", optional
    frequency: str = "daily"  # "daily" or "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def priority_rank(self) -> int:
        """Return a number for sorting: high=3, medium=2, low=1."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        pass


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    day_start: str = "08:00"  # "HH:MM" when the owner's day starts
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, name: str) -> None:
        """Remove a pet by its name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks for all of this owner's pets."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self) -> list[tuple[str, Task, str]]:
        """Build today's plan as an ordered list of (start time, task, reason)."""
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority and preferred time."""
        pass

    def filter_tasks(self, tasks: list[Task]) -> list[Task]:
        """Keep only the tasks that fit in the owner's available time."""
        pass

    def detect_conflicts(self, plan: list[tuple[str, Task, str]]) -> list[str]:
        """Return warnings for tasks whose time slots overlap."""
        pass

    def explain_plan(self, plan: list[tuple[str, Task, str]]) -> str:
        """Return a readable explanation of the plan and why each task was chosen."""
        pass
