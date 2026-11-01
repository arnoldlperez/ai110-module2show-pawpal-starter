"""PawPal+ logic layer: classes for owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field
from datetime import date

PRIORITY_RANKS = {"high": 3, "medium": 2, "low": 1}


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
        self.last_completed = today

    def is_due(self, today: date) -> bool:
        """Return True if the task still needs doing, based on frequency and last_completed."""
        if self.last_completed is None:
            return True
        days_since = (today - self.last_completed).days
        if self.frequency == "weekly":
            return days_since >= 7
        return days_since >= 1

    def priority_rank(self) -> int:
        """Return a number for sorting: high=3, medium=2, low=1."""
        return PRIORITY_RANKS.get(self.priority, 0)


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


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
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by its name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> list[PetTask]:
        """Return (pet, task) pairs for all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.skipped: list[PetTask] = []  # filled by generate_plan()

    @staticmethod
    def to_minutes(hhmm: str) -> int:
        """Convert "HH:MM" to minutes since midnight, e.g. "08:30" -> 510."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def to_hhmm(minutes: int) -> str:
        """Convert minutes since midnight back to "HH:MM", e.g. 510 -> "08:30"."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def generate_plan(self, today: date) -> list[PlanItem]:
        """Build today's plan from the tasks that are due, in order."""
        due = [(pet, task) for pet, task in self.owner.get_all_tasks() if task.is_due(today)]
        ordered = self.sort_tasks(due)
        chosen = self.filter_tasks(ordered)
        self.skipped = [pt for pt in ordered if pt not in chosen]

        plan: list[PlanItem] = []
        busy: list[tuple[int, int]] = []  # (start, end) in minutes

        # Tasks with a preferred time go exactly there first.
        for pet, task in chosen:
            if task.preferred_time is not None:
                start = self.to_minutes(task.preferred_time)
                busy.append((start, start + task.duration_minutes))
                reason = f"{task.priority} priority, scheduled at its preferred time"
                plan.append((task.preferred_time, pet, task, reason))

        # Flexible tasks fill the earliest open gap from the start of the day.
        for pet, task in chosen:
            if task.preferred_time is None:
                start = self._first_open_slot(task.duration_minutes, busy)
                busy.append((start, start + task.duration_minutes))
                reason = f"{task.priority} priority, placed in the first open slot"
                plan.append((self.to_hhmm(start), pet, task, reason))

        plan.sort(key=lambda item: self.to_minutes(item[0]))
        return plan

    def _first_open_slot(self, duration: int, busy: list[tuple[int, int]]) -> int:
        """Return the earliest start at or after day_start that doesn't overlap a busy slot."""
        start = self.to_minutes(self.owner.day_start)
        moved = True
        while moved:
            moved = False
            for busy_start, busy_end in busy:
                if start < busy_end and start + duration > busy_start:
                    start = busy_end
                    moved = True
        return start

    def sort_tasks(self, tasks: list[PetTask]) -> list[PetTask]:
        """Order tasks by priority and preferred time."""
        def key(pet_task: PetTask) -> tuple:
            task = pet_task[1]
            preferred = self.to_minutes(task.preferred_time) if task.preferred_time else 24 * 60
            return (-task.priority_rank(), preferred, task.duration_minutes)

        return sorted(tasks, key=key)

    def filter_tasks(self, tasks: list[PetTask]) -> list[PetTask]:
        """Keep only the tasks that fit in the owner's available time (expects sorted input)."""
        remaining = self.owner.available_minutes
        kept = []
        for pet, task in tasks:
            if task.duration_minutes <= remaining:
                kept.append((pet, task))
                remaining -= task.duration_minutes
        return kept

    def detect_conflicts(self, plan: list[PlanItem]) -> list[str]:
        """Return warnings for tasks whose time slots overlap."""
        warnings = []
        for i, (start_a, pet_a, task_a, _) in enumerate(plan):
            a_start = self.to_minutes(start_a)
            a_end = a_start + task_a.duration_minutes
            for start_b, pet_b, task_b, _ in plan[i + 1:]:
                b_start = self.to_minutes(start_b)
                b_end = b_start + task_b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"{pet_a.name}'s {task_a.title} ({start_a}-{self.to_hhmm(a_end)}) overlaps "
                        f"{pet_b.name}'s {task_b.title} ({start_b}-{self.to_hhmm(b_end)})"
                    )
        return warnings

    def explain_plan(self, plan: list[PlanItem]) -> str:
        """Return a readable explanation of the plan and why each task was chosen."""
        used = sum(task.duration_minutes for _, _, task, _ in plan)
        lines = [
            f"Today's Schedule for {self.owner.name} "
            f"({used} of {self.owner.available_minutes} min used)",
            "-" * 60,
        ]
        if not plan:
            lines.append("  No tasks scheduled.")
        for start, pet, task, reason in plan:
            end = self.to_hhmm(self.to_minutes(start) + task.duration_minutes)
            lines.append(f"  {start}-{end}  {pet.name:<8} {task.title:<18} ({task.duration_minutes} min)")
            lines.append(f"               why: {reason}")

        if self.skipped:
            lines.append("")
            lines.append("Skipped (not enough time left):")
            for pet, task in self.skipped:
                lines.append(f"  {pet.name}'s {task.title} ({task.duration_minutes} min, {task.priority} priority)")

        conflicts = self.detect_conflicts(plan)
        if conflicts:
            lines.append("")
            lines.append("Conflicts:")
            lines.extend(f"  WARNING: {c}" for c in conflicts)
        return "\n".join(lines)
