import streamlit as st

from auth.auth import authenticate


def login_page():

    st.title("📊 EBT Dashboard")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", use_container_width=True):

        user = authenticate(
            username,
            password
        )

        if user is None:

            st.error("Username atau Password salah.")

        else:

            st.session_state["logged_in"] = True

            st.session_state["username"] = user["USERNAME"]

            st.session_state["nama"] = user["NAMA"]

            st.session_state["role"] = user["ROLE"]

            st.rerun()