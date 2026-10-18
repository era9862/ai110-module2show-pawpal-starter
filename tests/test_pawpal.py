from datetime import date, time

import pytest

from pawpal_system import AddPet, Owner, Pet, Task, TodaysTasks


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


# --- Smarter scheduling -------------------------------------------------

DAY = date(2026, 10, 18)


def make_owner():
    owner = Owner("Jordan")
    adder = AddPet(owner)
    adder.add_pet("Rex", "dog")
    adder.add_pet("Whiskers", "cat")
    rex, whiskers = owner.get_schedules()
    return owner, rex, whiskers


def build_today(owner):
    today = TodaysTasks(DAY)
    today.build_from(owner.get_schedules())
    return today


def test_sort_by_time_orders_out_of_order_tasks():
    owner, rex, whiskers = make_owner()
    # Priorities run opposite to the clock, so only a real time sort passes.
    rex.add_task("Dinner", time(18, 0), 15, "high", due_date=DAY)
    rex.add_task("Walk", time(7, 30), 30, "low", due_date=DAY)
    whiskers.add_task("Meds", time(9, 0), 5, "medium", due_date=DAY)

    tasks = build_today(owner).sort_by_time()

    assert [t.title for t in tasks] == ["Walk", "Meds", "Dinner"]
    assert [t.due_time for t in tasks] == sorted(t.due_time for t in tasks)


def test_sort_breaks_time_ties_by_priority():
    owner, rex, _ = make_owner()
    rex.add_task("Low", time(9, 0), 5, "low", due_date=DAY)
    rex.add_task("High", time(9, 0), 5, "high", due_date=DAY)

    titles = [t.title for t in build_today(owner).sort_by_time()]

    assert titles == ["High", "Low"]


def test_filter_by_pet_and_status():
    owner, rex, whiskers = make_owner()
    walk = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY)
    rex.add_task("Dinner", time(18, 0), 15, "medium", due_date=DAY)
    whiskers.add_task("Meds", time(9, 0), 5, "high", due_date=DAY)
    today = build_today(owner)
    today.mark_done(walk)

    assert [t.title for t in today.filter_tasks(pet_name="Whiskers")] == ["Meds"]
    assert [t.title for t in today.filter_tasks(completed=True)] == ["Walk"]
    assert [t.title for t in today.filter_tasks(pet_name="Rex", completed=False)] == ["Dinner"]
    assert len(today.filter_tasks()) == 3


def test_daily_task_creates_next_occurrence_tomorrow():
    owner, rex, _ = make_owner()
    walk = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY, frequency="daily")

    next_task = rex.complete_task(walk)

    assert next_task is not None and next_task is not walk
    assert next_task.due_date == date(2026, 10, 19)
    assert next_task.completed is False
    assert next_task in rex.tasks and len(rex.tasks) == 2


def test_weekly_task_recurs_seven_days_later_across_month_end():
    owner, rex, _ = make_owner()
    task = rex.add_task("Bath", time(10, 0), 30, "low", due_date=date(2026, 10, 28), frequency="weekly")

    assert rex.complete_task(task).due_date == date(2026, 11, 4)


def test_one_off_task_does_not_recur():
    owner, rex, _ = make_owner()
    task = rex.add_task("Vet", time(10, 0), 60, "high", due_date=DAY)

    assert rex.complete_task(task) is None
    assert len(rex.tasks) == 1


def test_completing_twice_does_not_spawn_twice():
    owner, rex, _ = make_owner()
    walk = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY, frequency="daily")

    rex.complete_task(walk)
    assert rex.complete_task(walk) is None
    assert len(rex.tasks) == 2


def test_mark_done_on_todays_list_adds_next_occurrence_to_schedule():
    owner, rex, _ = make_owner()
    rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY, frequency="daily")
    today = build_today(owner)

    today.mark_done(today.tasks[0])

    assert len(rex.tasks) == 2
    assert len(build_today(owner).tasks) == 1  # tomorrow's copy is not due today


def test_conflict_warning_for_same_time_same_pet():
    owner, rex, _ = make_owner()
    rex.add_task("Walk", time(9, 0), 20, "high", due_date=DAY)
    rex.add_task("Feed", time(9, 0), 10, "high", due_date=DAY)

    warnings = build_today(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0] and "Rex" in warnings[0]


def test_conflict_warning_across_pets_and_overlapping_durations():
    owner, rex, whiskers = make_owner()
    rex.add_task("Walk", time(9, 0), 30, "high", due_date=DAY)
    whiskers.add_task("Meds", time(9, 15), 5, "high", due_date=DAY)

    warnings = build_today(owner).conflict_warnings()

    assert len(warnings) == 1 and "Rex and Whiskers" in warnings[0]


def test_back_to_back_tasks_are_not_conflicts():
    owner, rex, _ = make_owner()
    rex.add_task("Walk", time(9, 0), 30, "high", due_date=DAY)
    rex.add_task("Feed", time(9, 30), 10, "high", due_date=DAY)

    assert build_today(owner).conflict_warnings() == []


# --- Edge cases ---------------------------------------------------------

def test_pet_with_no_tasks_has_empty_schedule_and_no_warnings():
    owner, rex, _ = make_owner()
    today = build_today(owner)

    assert rex.get_tasks() == []
    assert today.tasks == []
    assert today.sort_by_time() == []
    assert today.get_pending() == []
    assert today.find_conflicts() == []
    assert today.conflict_warnings() == []


def test_filter_for_unknown_pet_returns_empty_list():
    owner, rex, _ = make_owner()
    rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY)

    assert build_today(owner).filter_tasks(pet_name="Nobody") == []


def test_same_exact_time_with_zero_duration_still_conflicts():
    owner, rex, whiskers = make_owner()
    rex.add_task("A", time(9, 0), 0, "high", due_date=DAY)
    whiskers.add_task("B", time(9, 0), 0, "high", due_date=DAY)

    assert len(build_today(owner).conflict_warnings()) == 1


def test_three_tasks_at_same_time_give_three_conflict_pairs():
    owner, rex, _ = make_owner()
    for name in ("A", "B", "C"):
        rex.add_task(name, time(9, 0), 10, "high", due_date=DAY)

    assert len(build_today(owner).find_conflicts()) == 3


def test_tasks_due_on_other_days_are_not_listed_or_flagged():
    owner, rex, _ = make_owner()
    rex.add_task("Today", time(9, 0), 30, "high", due_date=DAY)
    rex.add_task("Tomorrow", time(9, 0), 30, "high", due_date=date(2026, 10, 19))

    today = build_today(owner)

    assert [t.title for t in today.tasks] == ["Today"]
    assert today.conflict_warnings() == []


def test_daily_recurrence_crosses_year_end():
    owner, rex, _ = make_owner()
    task = rex.add_task("Walk", time(8, 0), 20, "high", due_date=date(2026, 12, 31), frequency="daily")

    assert rex.complete_task(task).due_date == date(2027, 1, 1)


def test_recurrence_chains_and_copies_the_task_details():
    owner, rex, _ = make_owner()
    walk = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY, frequency="daily")

    second = rex.complete_task(walk)
    third = rex.complete_task(second)

    assert third.due_date == date(2026, 10, 20)
    assert (third.title, third.due_time, third.duration, third.priority, third.pet) == (
        "Walk", time(8, 0), 20, "high", rex.pet,
    )


def test_completed_recurring_task_is_not_shown_as_done_tomorrow():
    owner, rex, _ = make_owner()
    walk = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY, frequency="daily")
    rex.complete_task(walk)

    tomorrow = TodaysTasks(date(2026, 10, 19))
    tomorrow.build_from(owner.get_schedules())

    assert [t.completed for t in tomorrow.tasks] == [False]


def test_new_task_without_a_date_is_due_today():
    owner, rex, _ = make_owner()
    task = rex.add_task("Walk", time(8, 0), 20, "high")

    assert task.due_date == date.today()


def test_completing_or_removing_a_task_from_the_wrong_place_raises():
    owner, rex, whiskers = make_owner()
    task = rex.add_task("Walk", time(8, 0), 20, "high", due_date=DAY)
    today = build_today(owner)

    with pytest.raises(ValueError):
        whiskers.complete_task(task)
    with pytest.raises(ValueError):
        whiskers.remove_task(task)
    with pytest.raises(ValueError):
        TodaysTasks(DAY).mark_done(task)  # never built, so it knows no schedules
    assert today.tasks == [task]


def test_add_task_rejects_bad_priority_and_frequency():
    owner, rex, _ = make_owner()

    with pytest.raises(ValueError):
        rex.add_task("Walk", time(8, 0), 20, "urgent")
    with pytest.raises(ValueError):
        rex.add_task("Walk", time(8, 0), 20, "high", frequency="monthly")
    assert rex.tasks == []


@pytest.mark.parametrize(
    "name, species, age",
    [("", "dog", 1), ("   ", "dog", 1), ("Rex", "", 1), ("Rex", "dog", -1)],
)
def test_add_pet_rejects_invalid_input(name, species, age):
    owner = Owner("Jordan")

    with pytest.raises(ValueError):
        AddPet(owner).add_pet(name, species, age)
    assert owner.get_pets() == [] and owner.get_schedules() == []


def test_add_pet_links_owner_and_creates_one_schedule():
    owner = Owner("Jordan")
    pet = AddPet(owner).add_pet("  Rex ", "dog", 3)

    assert pet.name == "Rex" and pet.owner is owner
    assert [s.pet for s in owner.get_schedules()] == [pet]
    assert owner.add_pet(pet) is owner.get_schedules()[0]  # re-adding does not duplicate
    assert len(owner.get_pets()) == 1


def test_remove_pet_drops_its_schedule_and_clears_owner():
    owner, rex, _ = make_owner()
    pet = rex.pet

    owner.remove_pet(pet)

    assert pet.owner is None
    assert rex not in owner.get_schedules() and pet not in owner.get_pets()
    with pytest.raises(ValueError):
        owner.remove_pet(pet)
