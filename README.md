# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation summary

The core logic lives in [pawpal_system.py](pawpal_system.py) (UML in [diagrams/uml.mmd](diagrams/uml.mmd)). It is plain Python with no UI dependency. [main.py](main.py) is a command-line demo that prints today's schedule, and [tests/test_pawpal.py](tests/test_pawpal.py) holds the tests. The Streamlit UI in `app.py` is not connected yet.

### How the classes work together

| Class | Role |
|-------|------|
| `Owner` | Holds the owner's details, their `Pet`s and one `PetSchedule` per pet. `add_pet()` registers a pet and creates its schedule. |
| `Pet` | Basic pet info (name, species, age, notes) and a link back to its `Owner`. |
| `Task` | One care task: title, pet, time, date, frequency (`once`/`daily`/`weekly`), duration, priority and completion. `mark_complete()` is the only place completion changes, and `is_due_on(day)` decides if it applies on a given day. |
| `AddPet` | Validates input, builds a `Pet` and hands it to `Owner.add_pet()`. |
| `PetSchedule` | One pet's task list. `add_task()` creates a `Task` for that pet, and `get_tasks()` returns them sorted by time. |
| `TodaysTasks` | The day's combined view. `build_from()` collects the tasks due on that day from all schedules. It can sort them by time and priority, list pending ones and detect overlapping tasks with `find_conflicts()`. |

### Flow

1. `AddPet` creates a `Pet` and registers it with the `Owner`, which creates and stores its `PetSchedule`.
2. Tasks are added through the pet's `PetSchedule`.
3. `TodaysTasks.build_from(owner.get_schedules())` gathers everything due today.
4. The result is sorted, checked for conflicts and displayed.

### Known limitation

A recurring task stays marked complete once finished, so a daily task done today still shows as done tomorrow. Tracking completion per day would fix this.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan - Sunday, October 18, 2026
============================================================
[ ] 07:30 AM  Morning walk   Rex         30 min  (high)
[ ] 09:00 AM  Medication     Whiskers     5 min  (high)
[ ] 06:00 PM  Dinner         Rex         15 min  (medium)
[ ] 06:10 PM  Playtime       Whiskers    20 min  (low)

Conflicts:
  ! Dinner (Rex) overlaps Playtime (Whiskers)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
