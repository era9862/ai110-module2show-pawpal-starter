from datetime import date, time

from pawpal_system import AddPet, Owner, TodaysTasks


def main() -> None:
    owner = Owner("Jordan", email="jordan@example.com")
    adder = AddPet(owner)

    rex = adder.add_pet("Rex", "dog", age=3)
    whiskers = adder.add_pet("Whiskers", "cat", age=5)

    schedules = {s.pet.name: s for s in owner.get_schedules()}
    schedules["Rex"].add_task("Morning walk", time(7, 30), 30, "high")
    schedules["Rex"].add_task("Dinner", time(18, 0), 15, "medium")
    schedules["Whiskers"].add_task("Medication", time(9, 0), 5, "high")
    schedules["Whiskers"].add_task("Playtime", time(18, 10), 20, "low")

    today = TodaysTasks(date.today())
    today.build_from(owner.get_schedules())

    print(f"Today's Schedule for {owner.name} - {today.date:%A, %B %d, %Y}")
    print("=" * 60)
    for task in today.sort_by_time():
        status = "x" if task.completed else " "
        print(
            f"[{status}] {task.due_time:%I:%M %p}  {task.title:<14} "
            f"{task.pet.name:<10} {task.duration:>3} min  ({task.priority})"
        )

    conflicts = today.find_conflicts()
    if conflicts:
        print("\nConflicts:")
        for a, b in conflicts:
            print(f"  ! {a.title} ({a.pet.name}) overlaps {b.title} ({b.pet.name})")


if __name__ == "__main__":
    main()
