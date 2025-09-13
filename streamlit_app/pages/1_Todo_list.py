import streamlit as st
import os
from supabase import create_client
from datetime import datetime

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="Todo List", layout="wide")

st.title("📝 Todo List")

if "user" not in st.session_state:
    st.warning("Please log in to access the Todo List.")
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

# If no tasks are found, show a message
if len(tasks.data) == 0:
    st.subheader("Great! You have no tasks assigned. 🎉")
else:
    # Create columns for Kanban board
    todo_col, in_progress_col, completed_col = st.columns([1, 1, 1])
    
    # Group tasks by status
    todo_tasks = [task for task in tasks.data if task['status'] == 'todo']
    in_progress_tasks = [task for task in tasks.data if task['status'] == 'in_progress']
    completed_tasks = [task for task in tasks.data if task['status'] == 'completed']
    
    # Function to display tasks as cards
    def display_tasks(column, tasks):
        with column:
            st.header(column == todo_col and "✏️ To Do" or column == in_progress_col and "🔄 In Progress" or "✅ Completed")
            for task in tasks:
                st.subheader(task['task'])
                st.write(f"**Description**: {task['description']}")
                deadline_str = task["deadline"]
                deadline_dt = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                formatted_deadline = deadline_dt.strftime("%d/%m/%Y")
                st.write(f"**Deadline**: {formatted_deadline}")
                # st.write(f"**Assigned To**: {task['recipient']}")
                st.write(f"**Assigned By**: {task['sender']}")
                st.markdown("---")

    # Display tasks in the respective columns
    display_tasks(todo_col, todo_tasks)
    display_tasks(in_progress_col, in_progress_tasks)
    display_tasks(completed_col, completed_tasks)