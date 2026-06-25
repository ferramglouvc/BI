import streamlit as st


def render_header():
    title_col, reset_col, logout_col = st.columns([8, 1, 1])

    with title_col:
        st.title("Calculadora BI")

    with reset_col:
        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    with logout_col:
        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
