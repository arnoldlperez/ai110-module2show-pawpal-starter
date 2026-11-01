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

    scheduler = Scheduler(owner)

    def complete_task(pet: Pet, task: Task) -> None:
        """Button callback: mark a task done and report when it comes back."""
        next_task = scheduler.mark_task_complete(pet, task, date.today())
        if next_task:
            st.session_state.flash = f"Completed {pet.name}'s {task.title}. Next one is due {next_task.due_date}."
        else:
            st.session_state.flash = f"Completed {pet.name}'s {task.title}."

    def remove_task(pet: Pet, task: Task) -> None:
        """Button callback: remove a task from its pet."""
        pet.remove_task(task.title)
        st.session_state.flash = f"Removed {task.title} from {pet.name}."

    # Callbacks run before the rerun, so the message from the last click shows here.
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["To do", "Done", "All"])

    completed = {"To do": False, "Done": True, "All": None}[status_filter]
    shown = scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name=None if pet_filter == "All pets" else pet_filter, completed=completed)
    )

    if not owner.get_all_tasks():
        st.info("No tasks yet. Add one above.")
    elif not shown:
        st.info("No tasks match these filters.")
    else:
        st.caption("Sorted by preferred time. Flexible tasks are listed last.")
        widths = [1.1, 1, 2, 1, 1.4, 1, 1]
        header = st.columns(widths)
        for col, label in zip(header, ["Time", "Pet", "Task", "Min", "Priority / repeat", "", ""]):
            col.markdown(f"**{label}**")
        for pet, task in shown:
            cols = st.columns(widths)
            cols[0].write(task.preferred_time or "flexible")
            cols[1].write(pet.name)
            cols[2].write(f"~~{task.title}~~" if task.completed else task.title)
            cols[3].write(str(task.duration_minutes))
            cols[4].write(f"{task.priority} / {task.frequency}")
            key = id(task)
            if task.is_due(date.today()):
                cols[5].button("Done", key=f"done_{key}", on_click=complete_task, args=(pet, task))
            elif not task.completed:
                cols[5].caption(f"due {task.due_date:%b %d}")
            cols[6].button("Remove", key=f"remove_{key}", on_click=remove_task, args=(pet, task))

st.divider()

st.subheader("Build Schedule")
st.caption("Uses tasks that are due today and not done yet.")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(date.today())
    conflicts = scheduler.detect_conflicts(plan)

    if not plan:
        st.info("Nothing to schedule. Add some tasks first, or check your available minutes.")
    else:
        used = sum(task.duration_minutes for _, _, task, _ in plan)
        if conflicts:
            # Shown above the plan so the owner sees it before reading the times.
            for conflict in conflicts:
                st.warning(f"⚠️ Time overlap: {conflict}. Consider moving one of these tasks to a different time.")
        else:
            st.success(f"Plan ready for {owner.name}: {len(plan)} tasks, {used} of {owner.available_minutes} min used.")

        st.table(
            [
                {
                    "start": start,
                    "end": Scheduler.to_hhmm(Scheduler.to_minutes(start) + task.duration_minutes),
                    "pet": pet.name,
                    "task": task.title,
                    "priority": task.priority,
                    "why": reason,
                }
                for start, pet, task, reason in plan
            ]
        )

    if scheduler.skipped:
        skipped = ", ".join(f"{pet.name}'s {task.title} ({task.duration_minutes} min)" for pet, task in scheduler.skipped)
        st.info(f"Didn't fit in today's time: {skipped}. Lower-priority tasks are dropped first.")

    with st.expander("Plain-text explanation"):
        st.code(scheduler.explain_plan(plan), language=None)
