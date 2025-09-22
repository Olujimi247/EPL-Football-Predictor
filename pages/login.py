import streamlit as st

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
            st.session_state["logged_in"] = True
            st.session_state["role"] = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password")

