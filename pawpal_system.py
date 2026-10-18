from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import List

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("once", "daily", "weekly")
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


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
    due_date: date = field(default_factory=date.today)  # the one day this instance is due
    frequency: str = "once"  # "once" | "daily" | "weekly"
    duration: int = 0  # minutes
    priority: str = "medium"  # "low" | "medium" | "high"
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def mark_complete(self) -> Task | None:
        """Mark done (the only place `completed` changes); return the next occurrence if recurring."""
        if self.completed:
            return None
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy due one day (daily) or seven days (weekly) later, or None if once."""
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        return Task(
            title=self.title,
            pet=self.pet,
            due_time=self.due_time,
            due_date=self.due_date + timedelta(days=days),
            frequency=self.frequency,
            duration=self.duration,
            priority=self.priority,
        )

    def is_due_on(self, day: date) -> bool:
        """Return True if this task instance is due on the given day."""
        return self.due_date == day

    def minute_range(self) -> tuple[int, int]:
        """Return (start, end) in minutes since midnight; a zero-length task counts as one minute."""
        start = self.due_time.hour * 60 + self.due_time.minute
        return start, start + max(self.duration, 1)


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
        """Create a task for this pet (due today unless a date is given) and add it to the schedule."""
        if priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")
        task = Task(
            title=title,
            pet=self.pet,
            due_time=due_time,
            due_date=due_date or date.today(),
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

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task and, if it recurs, add and return the next occurrence."""
        if not any(t is task for t in self.tasks):
            raise ValueError("task is not in this schedule")
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task

    def get_tasks(self) -> List[Task]:
        """Return this pet's tasks sorted by due time."""
        return sorted(self.tasks, key=lambda t: t.due_time)


class TodaysTasks:
    def __init__(self, day: date) -> None:
        self.date = day
        self.tasks: List[Task] = []
        self._schedules: List[PetSchedule] = []

    def build_from(self, schedules: List[PetSchedule]) -> None:
        """Collect tasks where task.is_due_on(self.date), remembering the schedules they came from."""
        self._schedules = list(schedules)
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

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> List[Task]:
        """Return today's tasks in time order, optionally only one pet's and/or only done or pending ones."""
        return [
            t
            for t in self.sort_by_time()
            if (pet_name is None or t.pet.name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def find_conflicts(self) -> List[tuple[Task, Task]]:
        """Return pairs of tasks (same or different pets) whose time ranges overlap."""
        ordered = self.sort_by_time()
        conflicts = []
        for i, a in enumerate(ordered):
            a_start, a_end = a.minute_range()
            for b in ordered[i + 1 :]:
                b_start, b_end = b.minute_range()
                if b_start >= a_end:
                    break  # sorted by start, so nothing later can overlap a
                if a_start < b_end:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(self) -> List[str]:
        """Return one readable warning per overlapping pair instead of raising an error."""
        warnings = []
        for a, b in self.find_conflicts():
            who = (
                f"for {a.pet.name}"
                if a.pet is b.pet
                else f"({a.pet.name} and {b.pet.name})"
            )
            warnings.append(
                f"Warning: '{a.title}' at {a.due_time:%H:%M} overlaps "
                f"'{b.title}' at {b.due_time:%H:%M} {who}"
            )
        return warnings

    def mark_done(self, task: Task) -> Task | None:
        """Complete a task through its schedule so a recurring task gets its next occurrence."""
        for schedule in self._schedules:
            if any(t is task for t in schedule.tasks):
                return schedule.complete_task(task)
        raise ValueError("task is not in today's list")
