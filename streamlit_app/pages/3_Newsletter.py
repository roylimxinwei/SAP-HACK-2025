# import streamlit as st
# from supabase import create_client
# import os
# from dotenv import load_dotenv
# import time
# import streamlit.components.v1 as components
# from datetime import datetime

# # Load environment variables
# load_dotenv()
# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# st.set_page_config(page_title="Fortnightly Newsletter")
# st.title("Fortnightly Newsletter")

# # --- Ensure user is logged in ---
# if "user" not in st.session_state:
#     st.warning("Please log in from the main page first!")
#     st.stop()

# user_email = st.session_state["user"].email

# # --- Fetch existing user profile from Supabase ---
# latest = supabase.table("newsletters") \
#         .select("markdown", "date_posted") \
#         .order("date_posted", desc=True) \
#         .limit(1) \
#         .execute()

# if latest.data:
#     newsletter = latest.data[0]

#     # print date posted
#     # st.write(f"Date Posted: {newsletter['date_posted']}")
#     # Get ISO timestamp from newsletter
#     iso_timestamp = newsletter['date_posted']

#     # Convert ISO 8601 string to datetime object
#     dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+08:00"))

#     # Format nicely, e.g., "Sep 13, 2025, 10:44 PM"
#     formatted_date = dt.strftime("%b %d, %Y, %I:%M %p")

#     # Display in Streamlit
#     st.markdown(f"**Date Posted:** {formatted_date}")

#     # render HTML content
#     # st.html(f"{newsletter['html']}")
#     # components.html(f'{newsletter["html"]}', scrolling=True, height=1500)
# #     components.html(f"""
# # <div style="font-family:sans-serif; color:black; max-width:800px; margin:auto; line-height:1.5;">
# # {newsletter['html']}
# # </div>
# # """, scrolling=True, height=1500)
#     st.markdown(newsletter['markdown'])


# else:
#     st.info("No newsletter available yet!")

import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

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
