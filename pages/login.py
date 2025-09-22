import streamlit as st

st.title("🔑 Login Page")

# Always show input fields
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Check if login button is clicked
if st.button("Login"):
    if "passwords" not in st.secrets:
        st.error("❌ No passwords set in Streamlit secrets. Please configure them.")
    elif username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
        st.session_state["authenticated"] = True
        st.session_state["role"] = username
        st.success(f"✅ Welcome {username}!")
        st.experimental_rerun()
    else:
        st.error("❌ Invalid username or password")






