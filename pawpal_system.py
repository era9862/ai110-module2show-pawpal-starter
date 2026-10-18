from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import List


@dataclass
class Owner:
    name: str
    email: str = ""
    phone: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""
    owner: Owner | None = None


@dataclass
class Task:
    title: str
    time: time
    duration: int = 0
    priority: str = "medium"
    completed: bool = False

    def mark_complete(self) -> None:
        pass


class AddPet:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def add_pet(self, name: str, species: str, age: int, notes: str) -> Pet:
        pass

    def validate(self) -> bool:
        pass


class PetSchedule:
    def __init__(self, pet: Pet) -> None:
        self.pet = pet
        self.tasks: List[Task] = []

    def add_task(self, title: str, time: time, duration: int, priority: str) -> Task:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def complete_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class TodaysTasks:
    def __init__(self, date: date) -> None:
        self.date = date
        self.tasks: List[Task] = []

    def build_from(self, schedules: List[PetSchedule]) -> None:
        pass

    def sort_by_time(self) -> List[Task]:
        pass

    def get_pending(self) -> List[Task]:
        pass

    def mark_done(self, task: Task) -> None:
        pass
