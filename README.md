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
| `TodaysTasks` | The day's combined view. `build_from()` collects the tasks due on that day from all schedules. It can sort, filter, warn about overlapping tasks and complete tasks (see Smarter Scheduling below). |

### Flow

1. `AddPet` creates a `Pet` and registers it with the `Owner`, which creates and stores its `PetSchedule`.
2. Tasks are added through the pet's `PetSchedule`.
3. `TodaysTasks.build_from(owner.get_schedules())` gathers everything due today.
4. The result is sorted, checked for conflicts and displayed.

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
python -m pytest
```

The 30 tests in [tests/test_pawpal.py](tests/test_pawpal.py) check the logic in `pawpal_system.py` directly, without the Streamlit UI.

| Area | What is checked |
|------|-----------------|
| Sorting | Tasks come back in chronological order, even when priorities run the opposite way. Tasks at the same time are ordered by priority. |
| Recurrence | Completing a daily task creates a copy due the next day. A weekly task recurs 7 days later. Dates roll over month and year ends. Chained completions work, and a one-off task does not recur. Completing a task twice does not create a second copy. The new copy keeps the title, time, duration, priority and pet and starts as not done. |
| Conflicts | Two tasks at the same time are flagged, for the same pet or different pets. Overlapping durations are flagged, and back-to-back tasks are not. Tasks due on another day are ignored. |
| Filtering | By pet, by done or pending, and both together. An unknown pet gives an empty list. |
| Edge cases | A pet with no tasks, an empty day, zero-length tasks at the same time, and three tasks at one time. Bad priority or frequency values, completing or removing a task from the wrong schedule, and blank names or negative ages are rejected. |
| Pets and owners | Adding a pet links it to its owner and creates one schedule. Re-adding it does not duplicate it. Removing a pet drops its schedule. |

I also checked that the tests can fail. I broke the code on purpose (wrong recurrence date, touching tasks counted as conflicts, sort ignoring time, double completion creating a copy) and each break made at least one test fail. The sort check first passed by luck, because the priorities in my test matched the time order. I fixed the test so only a real time sort passes.

Output of a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: .
collected 30 items

tests/test_pawpal.py ..............................                      [100%]

============================== 30 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4 out of 5)**

The scheduling logic is small, and the sorting, recurrence and conflict rules are covered by happy-path and edge-case tests that pass. I'm not giving 5 because of what is not covered:
- The Streamlit UI (`app.py`) has no automated tests.
- A task that runs past midnight (for example 23:50 for 30 minutes) is not compared with early tasks the next day.
- A skipped recurring task does not roll forward into the next day's list.
- Nothing is saved between sessions.

## 📐 Smarter Scheduling

`TodaysTasks` plays the scheduler role in this project, so the methods below live there unless noted. Run `python main.py` to see all of them in the terminal.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `TodaysTasks.sort_by_time()` | Orders by `due_time`, then by priority (high first). |
| Filtering | `TodaysTasks.filter_tasks(pet_name, completed)` | By pet name, by done/pending, or both. Results stay in time order. |
| Conflict handling | `TodaysTasks.find_conflicts()`, `TodaysTasks.conflict_warnings()` | Detects overlapping time ranges for the same or different pets and returns warning text instead of raising. |
| Recurring tasks | `Task.mark_complete()`, `Task.next_occurrence()`, `PetSchedule.complete_task()`, `TodaysTasks.mark_done()` | Completing a `daily` or `weekly` task creates the next copy. |

### Sorting
`sort_by_time()` uses `sorted()` with a tuple key, `(task.due_time, priority_rank)`. Times are `datetime.time` objects, so they compare correctly without string handling. Tasks at the same time are ordered high, then medium, then low priority.

### Filtering
`filter_tasks(pet_name=None, completed=None)` keeps a task only if it matches every filter given. Leave a filter as `None` to ignore it, for example `filter_tasks(completed=False)` for all pending tasks or `filter_tasks(pet_name="Rex")` for one pet.

### Conflict detection
`find_conflicts()` compares each task's time range (`Task.minute_range()`, start to start plus duration) with the tasks after it in time order. Two tasks conflict if their ranges overlap, so a 9:00 task of 30 minutes conflicts with one at 9:15 but not with one at 9:30. A task with no duration counts as one minute. `conflict_warnings()` turns each pair into a message such as `Warning: 'Medication' at 09:00 overlaps 'Brush fur' at 09:00 for Whiskers`, so the app can show it and carry on. The warning names both pets when they differ. Nothing is rescheduled automatically.

### Recurring tasks
Each `Task` is one occurrence on one `due_date`. `Task.mark_complete()` marks it done once and returns the next occurrence, built by `next_occurrence()` with `timedelta(days=1)` for `daily` or `timedelta(days=7)` for `weekly`. `PetSchedule.complete_task()` adds that new task to the schedule, and `TodaysTasks.mark_done()` finds the owning schedule and calls it. One-off tasks return nothing, and completing the same task twice does not create a second copy.

Because every occurrence has its own date and its own completion flag, a daily task finished today is not shown as done tomorrow.

### Tradeoff
A recurring task is only due on its exact `due_date`. If you skip a day, the missed occurrence does not roll forward into the next day's list.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
