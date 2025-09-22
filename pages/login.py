import streamlit as st

st.title("🔑 Login Page")

# --- Load usernames and passwords from secrets safely ---
if "passwords" in st.secrets:
    users = st.secrets["passwords"]
else:
    st.warning("⚠️ Using default demo credentials. (Secrets not found)")
    users = {"admin": "admin123", "guest": "guest123"}

    # --- Login form ---
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

if st.button("Login"):
    if username in users and users[username] == password:
        st.session_state["authenticated"] = True
        st.session_state["role"] = username   # track who logged in
        st.success(f"Welcome {username}!")
    else:
        st.error("Invalid username or password")





