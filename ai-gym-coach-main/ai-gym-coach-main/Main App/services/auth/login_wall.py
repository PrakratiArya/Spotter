import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    # Center the login form using columns
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #d2f000; font-weight: 800; letter-spacing: -0.05em;'>SPOTTER</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #999; margin-bottom: 2rem; letter-spacing: -0.02em;'>Your AI Real-time Gym Trainer</h4>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Name (unique)", placeholder="Enter a unique name (e.g. princekhunt)")
            submit_button = st.form_submit_button("Start Session", width="stretch")

        if submit_button:
            if not username:
                st.error("Name cannot be empty.")
                return False
            
            user = get_or_create_user(username)
        
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]

            st.rerun()

    return False