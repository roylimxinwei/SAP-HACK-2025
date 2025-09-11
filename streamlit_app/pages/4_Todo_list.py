import streamlit as st

st.set_page_config(page_title="Todo List")

st.title("📝 Todo List")

if "user" not in st.session_state:
    st.warning("Please log in to access the Todo List.")
    st.stop()