import streamlit as st

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn"):
        if username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
            st.session_state["logged_in"] = True
            st.session_state["role"] = username  # 'admin' or 'guest'
            st.success(f"Welcome {username}!")
            st.switch_page("home.py")  # redirect to Home
        else:
            st.error("Invalid username or password")

login()
