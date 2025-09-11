import streamlit as st

st.set_page_config(page_title="Onboarding Buddy")

st.title("🎒 Onboarding Buddy")

if "user" not in st.session_state:
    st.warning("Please log in to access the L&D Coach.")
    st.stop()
    
st.markdown("Ask about company policies, tools, and onboarding resources.")

