from datetime import date, time

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
    rex.add_task("Dinner", time(18, 0), 15, "medium", due_date=DAY)
    rex.add_task("Walk", time(7, 30), 30, "high", due_date=DAY)
    whiskers.add_task("Meds", time(9, 0), 5, "high", due_date=DAY)

    titles = [t.title for t in build_today(owner).sort_by_time()]

    assert titles == ["Walk", "Meds", "Dinner"]


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
