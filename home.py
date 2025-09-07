# 📄 app.py

import streamlit as st

OBbuddy = st.Page("pages/OBbuddy.py", title="Onboarding Buddy", icon=":material/add_circle:")
LDcoach = st.Page("pages/LDcoach.py", title="L&D Coach", icon=":material/delete:")

pg = st.navigation([OBbuddy, LDcoach])
st.set_page_config(page_title="AI hub", page_icon=":material/edit:")
pg.run()