import streamlit as st
import os
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo
import time

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="Taskboard", layout="wide")

st.title("📝 Taskboard")

if "user" not in st.session_state:
    st.warning("Please log in to access Taskboard.")
    st.stop()

# Identify the user to display user-specific tasks
user_email = st.session_state["user"].email
name = st.session_state.get("user_details", {}).get("name", "")
# Fetch tasks from Supabase table where recipient is the logged-in user
tasks = (
    supabase.table("tasks")
    .select("*")
    .or_(f"recipient.ilike.{user_email},recipient.ilike.{name}")
    .execute()
)

with st.expander("➕ Add a New Task", expanded=False):
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Title")
        description = st.text_area("Description")
        deadline = st.date_input("Deadline (optional)")
        status = st.selectbox("Status", ["todo", "in progress", "completed"])
        submitted = st.form_submit_button("Add Task")

        if submitted:
            deadline_str = None
            if deadline:
                deadline_dt = datetime.combine(deadline, datetime.min.time())
                deadline_str = deadline_dt.isoformat()

            supabase.table("tasks").insert({
                "task": task_name,
                "description": description,
                "deadline": deadline_str,
                "status": status,
                "recipient": user_email,  # assign to logged-in user
                "sender": user_email        # or whoever is assigning
            }).execute()

            st.session_state.toast_msg = "✅ Task added successfully!"
            st.rerun()


# If no tasks are found, show a message
if len(tasks.data) == 0:
    st.subheader("Great! You have no tasks assigned. 🎉")
else:
    # Create columns for Kanban board
    todo_col, in_progress_col, completed_col = st.columns([1, 1, 1])
    
    # Group tasks by status
    todo_tasks = [task for task in tasks.data if task['status'] == 'todo']
    in_progress_tasks = [task for task in tasks.data if task['status'] == 'in progress']
    completed_tasks = [task for task in tasks.data if task['status'] == 'completed']
    
    # Function to display tasks as cards
    def display_tasks(column, tasks):
        with column:
            st.header(
                column == todo_col and "✏️ To Do"
                or column == in_progress_col and "🔄 In Progress"
                or "✅ Completed"
            )

            for task in tasks:
                task_id = task["id"]  # assuming tasks table has an 'id' column

                # Unique key prefix for inputs and buttons
                key_prefix = f"task_{task_id}"

                # Check if task is being edited
                is_editing = st.session_state.get(f"{key_prefix}_editing", False)

                if is_editing:
                    # Editable fields
                    new_task = st.text_input("Task", task["task"], key=f"{key_prefix}_task")
                    new_desc = st.text_area("Description", task["description"], key=f"{key_prefix}_desc")
                    new_deadline = st.date_input(
                        "Deadline (SGT)",
                        datetime.fromisoformat(task["deadline"].replace("Z", "+00:00")).date()
                        if task.get("deadline") else None,
                        key=f"{key_prefix}_deadline"
                    )
                    new_status = st.selectbox(
                        "Status",
                        ["todo", "in progress", "completed"],
                        index=["todo", "in progress", "completed"].index(task["status"]),
                        key=f"{key_prefix}_status"
                    )

                    # Save / Cancel buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Update", key=f"{key_prefix}_update"):
                            # Convert deadline back to ISO (with 23:59:59 if only date chosen)
                            deadline_str = None
                            if new_deadline:
                                deadline_dt = datetime.combine(new_deadline, datetime.min.time())
                                deadline_str = deadline_dt.isoformat()

                            supabase.table("tasks").update({
                                "task": new_task,
                                "description": new_desc,
                                "deadline": deadline_str,
                                "status": new_status
                            }).eq("id", task_id).execute()

                            st.session_state[f"{key_prefix}_editing"] = False
                            st.toast("Task Updated!")
                            time.sleep(1)
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"{key_prefix}_cancel"):
                            st.session_state[f"{key_prefix}_editing"] = False
                            st.rerun()

                else:
                    # Normal view (read-only)
                    st.subheader(task["task"])
                    on = st.toggle(f"Show Details", key=f"{key_prefix}_toggle")
                    if on:
                        st.write(f"**Description**: {task['description']}")
                    if task.get("deadline"):
                        deadline_dt = datetime.fromisoformat(task["deadline"].replace("Z", "+00:00"))
                        sg_timezone = ZoneInfo("Asia/Singapore")
                        deadline_dt_sg = deadline_dt.astimezone(sg_timezone)
                        formatted_deadline = deadline_dt_sg.strftime("%d/%m/%Y %H:%M")
                    else:
                        formatted_deadline = "No deadline set"
                    st.write(f"**Deadline**: {formatted_deadline}")
                    st.write(f"**Assigned By**: {task['sender']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Edit", key=f"{key_prefix}_edit"):
                            st.session_state[f"{key_prefix}_editing"] = True
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete", key=f"{key_prefix}_delete"):
                            supabase.table("tasks").delete().eq("id", task_id).execute()
                            st.toast("Task deleted!")
                            time.sleep(1)
                            st.rerun()

                st.markdown("---")

    # Display tasks in the respective columns
    display_tasks(todo_col, todo_tasks)
    display_tasks(in_progress_col, in_progress_tasks)
    display_tasks(completed_col, completed_tasks)