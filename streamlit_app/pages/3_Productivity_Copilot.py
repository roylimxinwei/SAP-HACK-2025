import streamlit as st

st.set_page_config(page_title="Productivity Copilot")

st.title("🚀 Productivity Copilot")

if "user" not in st.session_state:
    st.warning("Please log in to access the Productivity Copilot.")
    st.stop()