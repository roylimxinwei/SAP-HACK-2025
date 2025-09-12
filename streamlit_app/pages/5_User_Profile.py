import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="📝 User Details")
st.title("📝 User Details / Personalization")

# --- Ensure user is logged in ---
if "user" not in st.session_state:
    st.warning("Please log in from the main page first!")
    st.stop()

user_email = st.session_state["user"].email

# --- Fetch existing user profile from Supabase ---
if "user_details" not in st.session_state:
    result = (
        supabase.table("user_profiles")
        .select("*")
        .eq("email", user_email)
        .maybe_single()
        .execute()
    )

    profile_data = result.data if result.data else {}  # Access .data for the actual dict
    st.session_state.user_details = {
        "name": profile_data.get("name", ""),
        "job_title": profile_data.get("job_title", ""),
        "team": profile_data.get("team", ""),
        "language": profile_data.get("language", "English"),
    }

details = st.session_state.user_details

# --- User details form ---
with st.form("user_details_form"):
    st.subheader("Update Your Profile")

    name = st.text_input("Preferred Name", value=details.get("name", ""))
    job_title = st.text_input("Job Title / Designation", value=details.get("job_title", ""))
    team = st.text_input("Team", value=details.get("team", ""))
    
    languages = ["English", "Chinese"]
    index = languages.index(details.get("language")) if details.get("language") in languages else 0
    language = st.selectbox("Preferred Language", options=languages, index=index)

    submitted = st.form_submit_button("Save Details")

    if submitted:
        # Upsert user details in Supabase
        supabase.table("user_profiles").upsert({
            "email": user_email,
            "name": name,
            "job_title": job_title,
            "team": team,
            "language": language
        }).execute()

        # Update session_state cache
        st.session_state.user_details.update({
            "name": name,
            "job_title": job_title,
            "team": team,
            "language": language
        })

        st.success("✅ Profile updated successfully!")
