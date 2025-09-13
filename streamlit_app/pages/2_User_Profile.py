import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

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

    if result is None: # create an emppty row in supabase
        st.info(f"Hey {user_email}, personalise your profile!", icon="👋")
         # --- User details form ---
        with st.form("create_profile_form"):
            st.subheader("Create Your Profile")

            name = st.text_input("Preferred Name", value="")
            job_title = st.text_input("Job Title / Designation", value="")
            team = st.text_input("Team", value="")

            submitted = st.form_submit_button("Confirm Details")

            if submitted:
                # Upsert user details in Supabase
                supabase.table("user_profiles").upsert({
                    "email": user_email,
                    "name": name,
                    "job_title": job_title,
                    "team": team
                }).execute()

                # ✅ Set session_state right away
                st.session_state.user_details = {
                    "name": name,
                    "job_title": job_title,
                    "team": team,
                }

                st.success("✅ Profile created successfully!")
                time.sleep(2)
                st.rerun()
    else:
        profile_data = result.data if result.data else {}  # Access .data for the actual dict
        st.session_state.user_details = {
            "name": profile_data.get("name", ""),
            "email": user_email,
            "job_title": profile_data.get("job_title", ""),
            "team": profile_data.get("team", "")
        }

if "user_details" in st.session_state:
    details = st.session_state.user_details

        # --- User details form ---
    with st.form("user_details_form"):
        st.subheader("Update Your Profile")
        name = st.text_input("Preferred Name", value=details.get("name", ""))
        job_title = st.text_input("Job Title / Designation", value=details.get("job_title", ""))
        team = st.text_input("Team", value=details.get("team", ""))
        submitted = st.form_submit_button("Update Details")
        if submitted:
            # Upsert user details in Supabase
            supabase.table("user_profiles").upsert({
                "email": user_email,
                "name": name,
                "job_title": job_title,
                "team": team
            }).execute()
            # Update session_state cache
            st.session_state.user_details.update({
                "name": name,
                "job_title": job_title,
                "team": team,
            })
            st.success("✅ Profile updated successfully!")
            time.sleep(2)
            st.rerun()
