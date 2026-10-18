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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
