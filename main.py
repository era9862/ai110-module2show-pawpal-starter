from datetime import date, time

from pawpal_system import AddPet, Owner, TodaysTasks


def show(title: str, tasks) -> None:
    print(f"\n{title}")
    print("-" * 60)
    if not tasks:
        print("  (none)")
    for task in tasks:
        status = "x" if task.completed else " "
        print(
            f"[{status}] {task.due_date:%b %d} {task.due_time:%I:%M %p}  {task.title:<14} "
            f"{task.pet.name:<10} {task.duration:>3} min  ({task.priority}, {task.frequency})"
        )


def main() -> None:
    owner = Owner("Jordan", email="jordan@example.com")
    adder = AddPet(owner)
    adder.add_pet("Rex", "dog", age=3)
    adder.add_pet("Whiskers", "cat", age=5)

    schedules = {s.pet.name: s for s in owner.get_schedules()}
    rex, whiskers = schedules["Rex"], schedules["Whiskers"]

    # Added deliberately out of time order.
    rex.add_task("Dinner", time(18, 0), 15, "medium", frequency="daily")
    whiskers.add_task("Playtime", time(18, 10), 20, "low")  # overlaps Dinner
    rex.add_task("Morning walk", time(7, 30), 30, "high", frequency="daily")
    whiskers.add_task("Medication", time(9, 0), 5, "high", frequency="weekly")
    whiskers.add_task("Brush fur", time(9, 0), 10, "low")  # same time as Medication

    today = TodaysTasks(date.today())
    today.build_from(owner.get_schedules())
    print(f"Today's Schedule for {owner.name} - {today.date:%A, %B %d, %Y}")

    show("Sorted by time", today.sort_by_time())
    show("Filtered: Rex only", today.filter_tasks(pet_name="Rex"))

    print("\nConflict warnings")
    print("-" * 60)
    for warning in today.conflict_warnings() or ["(none)"]:
        print(f"  {warning}")

    # Completing a recurring task schedules the next occurrence automatically.
    walk = today.filter_tasks(pet_name="Rex")[0]
    next_walk = today.mark_done(walk)
    show("After completing 'Morning walk': done tasks", today.filter_tasks(completed=True))
    show("Still pending", today.filter_tasks(completed=False))
    print(f"\nNext 'Morning walk' was created for {next_walk.due_date:%A, %B %d}")


if __name__ == "__main__":
    main()
