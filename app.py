from datetime import date, datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks for the day based on your time and their priorities.")

# Streamlit reruns this script on every click, so keep the Owner in session_state
# and only create it the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90, day_start="07:00")
owner: Owner = st.session_state.owner

st.subheader("Owner")
col1, col2, col3 = st.columns(3)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input("Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes)
    )
with col3:
    start = st.time_input("Day starts at", value=datetime.strptime(owner.day_start, "%H:%M").time())
    owner.day_start = start.strftime("%H:%M")

st.divider()

st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif any(p.name == pet_name.strip() for p in owner.pets):
            st.error(f"{pet_name.strip()} is already added.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.table([{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.caption("Add a pet first, then you can add tasks for it.")
else:
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            task_title = st.text_input("Task title", value="Morning walk")
            category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            has_time = st.checkbox("Set a preferred time")
            preferred = st.time_input("Preferred time", value=datetime.strptime("08:00", "%H:%M").time())
        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                pet = next(p for p in owner.pets if p.name == task_pet)
                pet.add_task(
                    Task(
                        title=task_title.strip(),
                        duration_minutes=int(duration),
                        priority=priority,
                        category=category,
                        preferred_time=preferred.strftime("%H:%M") if has_time else None,
                        frequency=frequency,
                    )
                )
                st.success(f"Added {task_title.strip()} for {pet.name}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.table(
            [
                {
                    "pet": pet.name,
                    "task": task.title,
                    "minutes": task.duration_minutes,
                    "priority": task.priority,
                    "time": task.preferred_time or "flexible",
                    "frequency": task.frequency,
                }
                for pet, task in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(date.today())

    if not plan:
        st.info("Nothing to schedule. Add some tasks first, or check your available minutes.")
    else:
        used = sum(task.duration_minutes for _, _, task, _ in plan)
        st.markdown(f"**Today's plan for {owner.name}** ({used} of {owner.available_minutes} min used)")
        st.table(
            [
                {
                    "start": start,
                    "end": Scheduler.to_hhmm(Scheduler.to_minutes(start) + task.duration_minutes),
                    "pet": pet.name,
                    "task": task.title,
                    "why": reason,
                }
                for start, pet, task, reason in plan
            ]
        )

    for pet, task in scheduler.skipped:
        st.warning(f"Skipped {pet.name}'s {task.title} ({task.duration_minutes} min): not enough time left.")
    for conflict in scheduler.detect_conflicts(plan):
        st.error(f"Conflict: {conflict}")

    with st.expander("Plain-text explanation"):
        st.code(scheduler.explain_plan(plan), language=None)
