import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
import requests, uuid

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

test_n8n_webhook_url = os.getenv("TEST_N8N_WEBHOOK_URL")
prod_n8n_webhook_url = os.getenv("PROD_N8N_WEBHOOK_URL")

# --- Sign up function ---
def signup(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

# --- Login function ---
def login(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

# --- Logout function ---
def logout():
    supabase.auth.sign_out()

st.title("🤖 Smart Agent Playground (S.A.P)")
st.set_page_config(page_title="(S.A.P) Home")

if "user" not in st.session_state:
    
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sign Up":
        st.subheader("Create New Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            res = signup(email, password)
            if res.user:
                st.success("✅ Account created! Please login.")
            else:
                st.error(res)

    elif choice == "Login":
        st.subheader("Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            res = login(email, password)
            if res.user:
                st.session_state["user"] = res.user
                st.success(f"Welcome {res.user.email} 👋")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Show logged-in state ---
if "user" in st.session_state:
    with st.sidebar:
        st.write("Logged in as:", st.session_state["user"].email)
        if st.button("Logout"):
            logout()
            st.session_state.pop("user")
            st.success("Logged out successfully!")
            st.rerun()

    # # Display existing messages
    # for msg in st.session_state.messages:
    #     with st.chat_message(msg["role"]):
    #         st.markdown(msg["content"])
    
    # Retrieve previous messages from Supabase (using user_email for message history)
    messages_data = supabase.table("chat_messages") \
        .select("*") \
        .eq("user_email", st.session_state["user"].email) \
        .order("timestamp", desc=False) \
        .execute()

    if messages_data.data:
        st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages_data.data]
    else:
        st.session_state.messages = []

    # Display existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Create or ensure a unique session ID (this can be done with a UUID)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Still can keep it for session-specific tracking if needed

    # Chat input box
    if prompt := st.chat_input("Say something..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # # Generate bot response (dummy example)
        # response = f"I heard you say: **{prompt}**"
        # st.session_state.messages.append({"role": "assistant", "content": response})
        # with st.chat_message("assistant"):
        #     st.markdown(response)


        #TODO: might need to make user personalisation first
        result = (
            supabase.table("user_profiles")
            .select("*")
            .eq("email", st.session_state["user"].email)
            .maybe_single()
            .execute()
        )

        profile_data = result.data or {}

        user_details = {
            "email": profile_data.get("email"),
            "name": profile_data.get("name"),
            "job_title": profile_data.get("job_title"),
            "team": profile_data.get("team")
        }

        payload = {
            "sessionId": st.session_state.session_id,
            "chatInput": prompt,
            "user_details": user_details
        }

        # st.write(payload)
        with st.spinner("S.A.P is thinking..."):
            response = requests.post(prod_n8n_webhook_url, json=payload)

        if response.status_code == 200:
            # st.success("Response from n8n:") # are we going to keep this?
            # with st.chat_message("assistant"):
            #     st.markdown(response.json()[0]["output"])
            # # st.write(response.json())  # or .text depending on your n8n response
            bot_reply = response.json()[0]["output"]  # adapt if n8n response shape differs

            # Store user message in Supabase with user_email and session_id
            supabase.table("chat_messages").insert({
                "user_email": st.session_state["user"].email,  # Link message to the logged-in user
                "session_id": st.session_state.session_id,
                "role": "user",
                "content": prompt
            }).execute()

            # Store assistant reply in Supabase
            supabase.table("chat_messages").insert({
                "user_email": st.session_state["user"].email,  # Link message to the logged-in user
                "session_id": st.session_state.session_id,
                "role": "assistant",
                "content": bot_reply
            }).execute()
            
            # Save assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            # Show assistant reply in a bubble
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

        else:
            st.error(f"Error: {response.status_code} {response.text}")

