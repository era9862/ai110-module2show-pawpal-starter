from datetime import date, time

import streamlit as st

from pawpal_system import AddPet, Owner, TodaysTasks

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# One Owner for the whole session; Streamlit re-runs this script on every click,
# so it is only created if the session "vault" does not already hold one.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a Pet")
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
    st.write("Your pets:")
    st.table(
        [{"name": p.name, "species": p.species, "age": p.age, "notes": p.notes}
         for p in owner.get_pets()]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
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
            due_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"], index=1)
        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("A task needs a title.")
            else:
                schedules[pet_choice].add_task(
                    task_title.strip(),
                    due_time,
                    int(duration),
                    priority,
                    due_date=date.today(),
                    frequency=frequency,
                )
                st.success(f"Added '{task_title.strip()}' for {schedules[pet_choice].pet.name}.")

    all_tasks = [t for s in schedules for t in s.get_tasks()]
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [{"pet": t.pet.name, "task": t.title, "time": t.due_time.strftime("%I:%M %p"),
              "minutes": t.duration, "priority": t.priority, "repeats": t.frequency}
             for t in all_tasks]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
if st.button("Generate schedule"):
    today = TodaysTasks(date.today())
    today.build_from(owner.get_schedules())
    ordered = today.sort_by_time()
    if not ordered:
        st.info("Nothing is due today.")
    else:
        st.table(
            [{"time": t.due_time.strftime("%I:%M %p"), "pet": t.pet.name, "task": t.title,
              "minutes": t.duration, "priority": t.priority, "done": t.completed}
             for t in ordered]
        )
        for a, b in today.find_conflicts():
            st.warning(
                f"Conflict: {a.title} ({a.pet.name}) overlaps {b.title} ({b.pet.name})."
            )
