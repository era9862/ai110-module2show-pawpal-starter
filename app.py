from datetime import date, time

import streamlit as st

from pawpal_system import AddPet, Owner, TodaysTasks

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "Add your pets, schedule their care tasks, and get a sorted, conflict-checked plan for today."
)

# One Owner for the whole session; Streamlit re-runs this script on every click,
# so it is only created if the session "vault" does not already hold one.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

# --- Owner and pets -----------------------------------------------------------------

st.subheader("1. Owner and pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    col1, col2 = st.columns(2)
    with col1:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col2:
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    notes = st.text_input("Notes (optional)")
    if st.form_submit_button("Add pet"):
        try:
            AddPet(owner).add_pet(pet_name, species, int(age), notes)
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as err:
            st.error(str(err))

if owner.get_pets():
    st.table(
        [
            {"Name": p.name, "Species": p.species, "Age": p.age, "Notes": p.notes}
            for p in owner.get_pets()
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Scheduling a task --------------------------------------------------------------

st.subheader("2. Schedule a task")
schedules = owner.get_schedules()
if not schedules:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task_form"):
        pet_choice = st.selectbox(
            "Pet", range(len(schedules)), format_func=lambda i: schedules[i].pet.name
        )
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            due_date = st.date_input("Date", value=date.today())
        with col2:
            due_time = st.time_input("Time", value=time(8, 0))
        with col3:
            duration = st.number_input("Minutes", min_value=1, max_value=240, value=20)
        col4, col5 = st.columns(2)
        with col4:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col5:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"], index=1)
        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("A task needs a title.")
            else:
                schedule = schedules[pet_choice]
                schedule.add_task(
                    task_title.strip(), due_time, int(duration), priority,
                    due_date=due_date, frequency=frequency,
                )
                st.success(f"Added '{task_title.strip()}' for {schedule.pet.name}.")

st.divider()

# --- Today's schedule ---------------------------------------------------------------

st.subheader("3. Today's schedule")

today = TodaysTasks(date.today())
today.build_from(owner.get_schedules())

# Message left by a "Done" click on the previous run.
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

if not today.tasks:
    st.info("Nothing is scheduled for today. Add a task above.")
else:
    pending_count = len(today.get_pending())
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks today", len(today.tasks))
    col2.metric("Pending", pending_count)
    col3.metric("Done", len(today.tasks) - pending_count)

    # Conflict warnings come first so the owner sees problems before the plan.
    warnings = today.conflict_warnings()
    if warnings:
        st.warning(
            f"**{len(warnings)} scheduling conflict{'s' if len(warnings) != 1 else ''} found.** "
            "Remove one task in each pair (use the Remove buttons below) and add it again at a free time."
        )
        for message in warnings:
            st.warning(message.removeprefix("Warning: "), icon="⚠️")
    else:
        st.success("No conflicts - everything today fits.")

    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Show pet", ["All pets"] + [p.name for p in owner.get_pets()]
        )
    with col2:
        status_filter = st.radio("Show status", ["All", "Pending", "Done"], horizontal=True)

    shown = today.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Done": True}[status_filter],
    )
    if shown:
        st.table(
            [
                {
                    "Time": t.due_time.strftime("%I:%M %p"),
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Minutes": t.duration,
                    "Priority": t.priority,
                    "Repeats": t.frequency,
                    "Status": "✅ Done" if t.completed else "⏳ Pending",
                }
                for t in shown
            ]
        )
    else:
        st.info("No tasks match those filters.")

    pending = [t for t in shown if not t.completed]
    if pending:
        st.write("Mark a task done, or remove it:")
        for task in pending:
            label = f"{task.due_time:%I:%M %p} - {task.title} ({task.pet.name})"
            done_col, remove_col = st.columns([4, 1])
            if done_col.button(f"✔ {label}", key=f"done_{task.id}"):
                next_task = today.mark_done(task)
                message = f"Marked '{task.title}' done for {task.pet.name}."
                if next_task:
                    message += f" Next one is scheduled for {next_task.due_date:%A, %b %d}."
                st.session_state.flash = message
                st.rerun()
            if remove_col.button("Remove", key=f"remove_{task.id}"):
                owner_schedule = next(s for s in owner.get_schedules() if s.pet is task.pet)
                owner_schedule.remove_task(task)
                st.session_state.flash = f"Removed '{task.title}' for {task.pet.name}."
                st.rerun()

# --- Everything scheduled, any day --------------------------------------------------

with st.expander("All scheduled tasks (every day)"):
    every_task = sorted(
        (t for s in owner.get_schedules() for t in s.tasks),
        key=lambda t: (t.due_date, t.due_time),
    )
    if every_task:
        st.table(
            [
                {
                    "Date": t.due_date.strftime("%a %b %d"),
                    "Time": t.due_time.strftime("%I:%M %p"),
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Repeats": t.frequency,
                    "Status": "✅ Done" if t.completed else "⏳ Pending",
                }
                for t in every_task
            ]
        )
    else:
        st.write("No tasks yet.")
