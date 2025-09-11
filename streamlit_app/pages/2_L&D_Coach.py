import streamlit as st

st.set_page_config(page_title="L&D Coach")

st.title("📚 L&D Coach")

if "user" not in st.session_state:
    st.warning("Please log in to access the L&D Coach.")
    st.stop()


st.markdown("Ask about upskilling, internal learning resources, or career development.")
