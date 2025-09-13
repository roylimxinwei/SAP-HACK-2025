
import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="Fortnightly Newsletter")
st.title("Fortnightly Newsletter")

# --- Ensure user is logged in ---
if "user" not in st.session_state:
    st.warning("Please log in from the main page first!")
    st.stop()

user_email = st.session_state["user"].email

# --- Fetch the latest newsletter for this user ---
latest = (
    supabase.table("newsletters")
    .select("markdown", "date_posted")
    .eq("email", user_email)  # Filter by logged-in user
    .order("date_posted", desc=True)
    .limit(1)
    .execute()
)

if latest.data:
    newsletter = latest.data[0]

    # Convert ISO 8601 string to datetime object
    iso_timestamp = newsletter['date_posted']
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+08:00"))

    # Format nicely, e.g., "Sep 13, 2025, 10:44 PM"
    formatted_date = dt.strftime("%b %d, %Y, %I:%M %p")

    # Display date and markdown content
    st.markdown(f"**Date Posted:** {formatted_date}\n\n")
    st.markdown(newsletter['markdown'])
else:
    st.info("No newsletter available yet for you!")
