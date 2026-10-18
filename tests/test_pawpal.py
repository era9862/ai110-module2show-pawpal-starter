from datetime import time

from pawpal_system import Owner, Pet, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", Pet("Rex", "dog"), time(7, 30))
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    owner = Owner("Jordan")
    pet = Pet("Rex", "dog")
    schedule = owner.add_pet(pet)
    assert len(schedule.get_tasks()) == 0

    schedule.add_task("Dinner", time(18, 0), 15, "medium")

    assert len(schedule.get_tasks()) == 1
