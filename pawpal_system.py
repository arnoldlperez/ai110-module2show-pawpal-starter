"""PawPal+ logic layer: classes for owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care task, like a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str = "other"  # e.g. "walk", "feeding", "meds", "grooming"
    preferred_time: str | None = None  # "HH:MM", optional
    frequency: str = "daily"  # "daily" or "weekly"
    last_completed: date | None = None

    def mark_complete(self, today: date) -> None:
        """Record that this task was done on the given day."""
        pass

    def is_due(self, today: date) -> bool:
        """Return True if the task still needs doing, based on frequency and last_completed."""
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


# A task paired with the pet it belongs to, so the plan can say whose task it is.
PetTask = tuple[Pet, Task]
# One entry in the daily plan: (start time "HH:MM", pet, task, reason).
PlanItem = tuple[str, Pet, Task, str]


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

    def get_all_tasks(self) -> list[PetTask]:
        """Return (pet, task) pairs for all of this owner's pets."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    @staticmethod
    def to_minutes(hhmm: str) -> int:
        """Convert "HH:MM" to minutes since midnight, e.g. "08:30" -> 510."""
        pass

    @staticmethod
    def to_hhmm(minutes: int) -> str:
        """Convert minutes since midnight back to "HH:MM", e.g. 510 -> "08:30"."""
        pass

    def generate_plan(self, today: date) -> list[PlanItem]:
        """Build today's plan from the tasks that are due, in order."""
        pass

    def sort_tasks(self, tasks: list[PetTask]) -> list[PetTask]:
        """Order tasks by priority and preferred time."""
        pass

    def filter_tasks(self, tasks: list[PetTask]) -> list[PetTask]:
        """Keep only the tasks that fit in the owner's available time."""
        pass

    def detect_conflicts(self, plan: list[PlanItem]) -> list[str]:
        """Return warnings for tasks whose time slots overlap."""
        pass

    def explain_plan(self, plan: list[PlanItem]) -> str:
        """Return a readable explanation of the plan and why each task was chosen."""
        pass
