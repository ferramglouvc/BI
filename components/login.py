import streamlit as st
import uuid


def init_auth_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "username" not in st.session_state:
        st.session_state.username = None

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "active_users" not in st.session_state:
        st.session_state.active_users = {}


def render_login(users: dict):
    init_auth_state()

    if not st.session_state.authenticated:
        st.title("Login")

        with st.form("login_form"):
            user = st.text_input("User")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            if user in users and pwd == users[user]:
                if user in st.session_state.active_users:
                    st.error("This user is already logged in.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.session_state.active_users[user] = st.session_state.session_id
                    st.rerun()
            else:
                st.error("Invalid credentials")

        st.stop()


def validate_session():
    if st.session_state.username:
        active_id = st.session_state.active_users.get(st.session_state.username)
        if active_id != st.session_state.session_id:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.error("Your session was replaced by another login.")
            st.stop()


def logout_current_user():
    user = st.session_state.username
    if user in st.session_state.active_users:
        del st.session_state.active_users[user]

    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()
