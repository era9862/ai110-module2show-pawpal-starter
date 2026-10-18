# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
1. Pets Schedule
2. Add a pet
3. Todays tasks

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, I changed the owner of the pet information and created pet and tasks as two different objects. Also, the schedule is under owner's info and pet is an object so owners could have more than one pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three things:

- **Time:** each task has a date, a start time and a duration. Time matters most because pet care runs on the clock, and a late medication is worse than a late play session. It decides the order of the plan and what counts as a conflict.
- **Priority** (low, medium, high): it only breaks ties between tasks at the same time. It does not decide which tasks are kept.
- **Frequency** (once, daily, weekly): it decides whether finishing a task creates the next one.

I did not model owner preferences or the owner's total free time. The scheduler orders and checks the tasks it is given. It does not choose which ones to drop.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler only **warns** about conflicts. It never moves or drops a task to fix them. `conflict_warnings()` reports every pair of tasks whose time ranges overlap, including different pets, and the owner decides what to do.

This is reasonable because a pet owner knows things the scheduler does not. They might walk the dog while the cat eats, or the vet visit might be fixed. An automatic fix could silently move a medication. A plain warning is also safe, because it can never crash the app or lose a task.

I also compare overlapping durations rather than only exact start times. That catches a 9:00 walk of 30 minutes running into a 9:15 medication, at the cost of a little more code. Within that, the AI suggested a shorter version using `itertools.combinations`. It reads better but compares every pair. I kept my loop, which stops early because the tasks are sorted, since it is still readable and does less work.

A second, smaller tradeoff: a recurring task is due only on its exact date, so a skipped day does not roll forward.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code as a pair programmer for the whole project, in this order:

1. **Design:** I asked for a Mermaid class diagram of my three classes (PetSchedule, AddPet, TodaysTasks), then asked for `Pet`, `Task` and `Owner` to be added as their own classes.
2. **Skeleton:** I had it turn the UML into Python class stubs in `pawpal_system.py`.
3. **Review:** I asked it to review its own skeleton for missing relationships and logic bottlenecks.
4. **Implementation:** I used its agent mode to fill in the method bodies, then to write `main.py`, two tests, docstrings and the README summary.

The most helpful prompts were specific and asked for one thing at a time ("add owner of the pets into this diagram", "review your skeleton for missing relationships"). Asking it to critique its own output was the most valuable prompt, because it caught problems I would not have seen in a skeleton with no logic.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**What the AI suggested, and what I accepted or changed**

- **Changed its first design.** Its first diagram used `Pet` and `Task` as types without defining them. I asked for them as separate classes, so the diagram now shows them.
- **Accepted its review findings.** The review said `Task` had no link to a `Pet`, nothing stored the schedules, `Task` had no date to decide what is "today", and there were four ways to complete a task. I said yes to all of the fixes, which added `Task.pet`, `Owner.schedules`, `due_date`/`frequency` and a single `Task.mark_complete()`.
- **Kept the Owner and Pet link in both directions.** The AI pointed out that `Owner.pets` and `Pet.owner` reference each other and offered to make it one-way. I kept both directions, and the fix was to exclude `Pet.owner` from comparisons.
- **Fixed the recurring-task limitation later.** The AI flagged that a recurring task stays complete once finished. When I added recurring tasks, each occurrence got its own date and completion flag, which removed the problem.

**How I verified it**

- **Reproduced the bug before trusting it.** The review claimed comparing two owners would recurse forever. The comparison raised a `RecursionError`, and after the fix it returned `True`.
- **Ran what it wrote.** After each step I checked the code actually ran: the module imported, `python3 main.py` printed the schedule, and `pytest` passed.
- **Read the output, not just the code.** In the demo, Dinner and Playtime overlapped and the conflict check reported them, which confirmed the overlap logic worked.

**c. AI strategy**

- **Most effective features:**
  - *Agent mode* made multi-file changes in one pass. Adding recurring tasks meant changing `Task`, `PetSchedule`, `TodaysTasks`, `main.py`, the tests and the UML together.
  - *Asking it to review its own output* found the `Owner`/`Pet` recursion bug and the missing `Task`-to-`Pet` link before they caused trouble.
  - *Running the code* after every change caught mistakes, such as a sorting test that passed even when the sort was broken.
- **A suggestion I changed or rejected:** the AI's first diagram used `Pet` and `Task` as types without defining them, so I asked for both as separate classes. Later it offered to make the `Owner`/`Pet` link one-way, and I kept both directions and excluded `Pet.owner` from comparisons instead. It also proposed a shorter `itertools.combinations` version of conflict detection. I kept the loop that stops early on sorted tasks, because it is still readable and does less work.
- **Separate chat sessions:** I did not use them. I did all phases in one long conversation, so I cannot say they helped. What kept me organized instead was that the project files carried the plan. The UML, the README and the tests recorded each decision, so I could check the AI's work against them. I would try separate sessions next time. A test-only session would not be anchored on how the code was written, and that is the kind of review that found the weak sorting test.
- **Being the lead architect:** the AI writes code quickly, but it does not know what the app is for. I had to decide which classes exist, who owns what, which tradeoffs are acceptable (warn about conflicts, never reschedule) and when something was good enough. The AI offered options, and my job was to choose, check and keep the design simple.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 30 automated tests that call the classes in `pawpal_system.py` directly, without the UI:

- **Sorting:** tasks come back in clock order, and ties are broken by priority.
- **Recurrence:** a daily task creates the next one for tomorrow and a weekly task recurs 7 days later, including across month and year ends. A one-off task does not recur, and completing a task twice does not create a second copy.
- **Conflicts:** same-time tasks, overlapping durations and tasks for different pets are flagged. Back-to-back tasks and tasks on other days are not.
- **Filtering and edge cases:** a pet with no tasks, an empty day, zero-length tasks, bad priority, frequency, name or age values, and completing a task from the wrong schedule.

These matter because the scheduler's value is in being right about order, repeats and overlaps, and a wrong date or a missed conflict would not be obvious when using the app. I also broke the code on purpose to check the tests can fail. That showed my first sorting test was too weak, so I rewrote it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

About 4 out of 5. All 30 tests pass, and breaking the code on purpose makes them fail. The reason it is not 5 is what is untested: the Streamlit UI has no automated tests, I only checked it by running it.

Next I would test:
- a task that runs past midnight, such as 23:50 for 30 minutes, against tasks early the next day
- what happens to a recurring task that was skipped for a day
- two pets with the same name
- very long task lists

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied that the scheduling logic is separate from the interface. The same classes run in the command-line demo, in the tests and in the Streamlit app, and the 30 tests mean I can change one without worrying about the others. Making each task a single dated occurrence also made recurrence simple and fixed a bug where a daily task stayed marked done the next day.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- Let a skipped recurring task roll forward into the next day's list instead of disappearing.
- Add editing a task's time in the UI, so a conflict can be fixed in one step. Right now you remove the task and add it again.
- Save the owner, pets and tasks between sessions.
- Make the scheduler help decide what to do. It only sorts and warns today, and it could use free time and priority to suggest which tasks to drop or move.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Write the design down first and keep it up to date, because it is the only way to judge what the AI produces. The UML, the tests and the README were how I noticed the missing links and the weak test. The AI is a fast pair programmer, but I stay responsible for the structure and for checking that it works.
