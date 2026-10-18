from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, time
from typing import List

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Owner:
    name: str
    email: str = ""
    phone: str = ""
    pets: List[Pet] = field(default_factory=list)
    schedules: List[PetSchedule] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> PetSchedule:
        """Register the pet, set pet.owner, and create and store its PetSchedule."""
        for schedule in self.schedules:
            if schedule.pet is pet:
                return schedule
        pet.owner = self
        self.pets.append(pet)
        schedule = PetSchedule(pet)
        self.schedules.append(schedule)
        return schedule

    def remove_pet(self, pet: Pet) -> None:
        """Remove the pet and its schedule from this owner."""
        if not any(p is pet for p in self.pets):
            raise ValueError(f"{pet.name} does not belong to {self.name}")
        self.pets = [p for p in self.pets if p is not pet]
        self.schedules = [s for s in self.schedules if s.pet is not pet]
        pet.owner = None

    def get_pets(self) -> List[Pet]:
        """Return a copy of this owner's pets."""
        return list(self.pets)

    def get_schedules(self) -> List[PetSchedule]:
        """Return a copy of this owner's pet schedules."""
        return list(self.schedules)


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""
    # compare/repr off: Owner <-> Pet is a cycle and would recurse forever.
    owner: Owner | None = field(default=None, repr=False, compare=False)


# eq=False: tasks compare by identity, so two "Feed at 8:00" tasks stay distinct.
@dataclass(eq=False)
class Task:
    title: str
    pet: Pet = field(repr=False)
    due_time: time
    due_date: date | None = None  # None = every day (recurring)
    frequency: str = "once"  # "once" | "daily" | "weekly"
    duration: int = 0  # minutes
    priority: str = "medium"  # "low" | "medium" | "high"
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def mark_complete(self) -> None:
        """The only place that changes `completed`."""
        self.completed = True

    def is_due_on(self, day: date) -> bool:
        """Return True if the task falls due on the given day."""
        if self.due_date is None:
            return True
        if day < self.due_date:
            return False
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            return (day - self.due_date).days % 7 == 0
        return day == self.due_date


class AddPet:
    """Validates input, then delegates to Owner.add_pet."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def add_pet(self, name: str, species: str, age: int = 0, notes: str = "") -> Pet:
        """Validate the details, create a Pet and register it with the owner."""
        if not self.validate(name, species, age):
            raise ValueError("A pet needs a name, a species and a non-negative age")
        pet = Pet(name.strip(), species.strip(), age, notes)
        self.owner.add_pet(pet)
        return pet

    def validate(self, name: str, species: str, age: int) -> bool:
        """Return True if the name and species are non-blank and the age is not negative."""
        return bool(name.strip()) and bool(species.strip()) and age >= 0


class PetSchedule:
    def __init__(self, pet: Pet) -> None:
        self.pet = pet
        self.tasks: List[Task] = []

    def add_task(
        self,
        title: str,
        due_time: time,
        duration: int,
        priority: str,
        due_date: date | None = None,
        frequency: str = "once",
    ) -> Task:
        """Create a task for this pet, validate it and add it to the schedule."""
        if priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")
        task = Task(
            title=title,
            pet=self.pet,
            due_time=due_time,
            due_date=due_date,
            frequency=frequency,
            duration=duration,
            priority=priority,
        )
        self.tasks.append(task)
        return task

    def remove_task(self, task: Task) -> None:
        """Remove a task from this schedule, raising ValueError if it is absent."""
        if not any(t is task for t in self.tasks):
            raise ValueError("task is not in this schedule")
        self.tasks = [t for t in self.tasks if t is not task]

    def complete_task(self, task: Task) -> None:
        """Delegates to task.mark_complete()."""
        if not any(t is task for t in self.tasks):
            raise ValueError("task is not in this schedule")
        task.mark_complete()

    def get_tasks(self) -> List[Task]:
        """Return this pet's tasks sorted by due time."""
        return sorted(self.tasks, key=lambda t: t.due_time)


class TodaysTasks:
    def __init__(self, day: date) -> None:
        self.date = day
        self.tasks: List[Task] = []

    def build_from(self, schedules: List[PetSchedule]) -> None:
        """Collect tasks where task.is_due_on(self.date)."""
        self.tasks = [
            task
            for schedule in schedules
            for task in schedule.tasks
            if task.is_due_on(self.date)
        ]

    def sort_by_time(self) -> List[Task]:
        """Order by due_time, then by priority."""
        return sorted(
            self.tasks, key=lambda t: (t.due_time, PRIORITY_RANK.get(t.priority, 1))
        )

    def get_pending(self) -> List[Task]:
        """Return today's incomplete tasks in time order."""
        return [t for t in self.sort_by_time() if not t.completed]

    def find_conflicts(self) -> List[tuple[Task, Task]]:
        """Pairs of tasks whose time ranges overlap."""

        def span(task: Task) -> tuple[int, int]:
            start = task.due_time.hour * 60 + task.due_time.minute
            return start, start + max(task.duration, 1)

        ordered = self.sort_by_time()
        conflicts = []
        for i, a in enumerate(ordered):
            a_start, a_end = span(a)
            for b in ordered[i + 1 :]:
                b_start, b_end = span(b)
                if b_start >= a_end:
                    break  # sorted by start, so nothing later can overlap a
                if a_start < b_end:
                    conflicts.append((a, b))
        return conflicts

    def mark_done(self, task: Task) -> None:
        """Delegates to task.mark_complete()."""
        if not any(t is task for t in self.tasks):
            raise ValueError("task is not in today's list")
        task.mark_complete()
