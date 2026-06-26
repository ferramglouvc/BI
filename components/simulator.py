import streamlit as st


def init_simulator_context(context_key, defaults):
    if st.session_state.get("sim_context") != context_key:
        st.session_state["sim_defaults"] = defaults
        st.session_state["sim_arrivals"] = defaults["arrivals"]
        st.session_state["sim_contracts"] = defaults["contracts"]
        st.session_state["sim_closing_rate"] = defaults["closing_rate"]
        st.session_state["sim_avg_price"] = defaults["avg_price"]
        st.session_state["sim_context"] = context_key


def request_simulator_reset():
    st.session_state["sim_reset_requested"] = True


def render_simulator():
    st.markdown(
        "<div class='section-title' style='margin-top:0rem;margin-bottom:0rem;'>Actuals Simulator</div>",
        unsafe_allow_html=True
    )

    # muy poco espacio arriba del bloque
    st.markdown("<div style='margin-top:-0.75rem;'></div>", unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns(2, gap="small")
    row2_col1, row2_col2 = st.columns(2, gap="small")

    with row1_col1:
        st.number_input(
            "Arrivals",
            key="sim_arrivals",
            value=float(st.session_state["sim_arrivals"]),
            step=1.0,
            format="%.0f",
            label_visibility="visible"
        )

    with row1_col2:
        st.number_input(
            "Contracts",
            key="sim_contracts",
            value=float(st.session_state["sim_contracts"]),
            step=1.0,
            format="%.0f",
            label_visibility="visible"
        )

    with row2_col1:
        st.number_input(
            "Closing Rate %",
            key="sim_closing_rate",
            value=float(st.session_state["sim_closing_rate"]),
            step=0.1,
            format="%.1f",
            label_visibility="visible"
        )

    with row2_col2:
        st.number_input(
            "Average Price ($)",
            key="sim_avg_price",
            value=float(st.session_state["sim_avg_price"]),
            step=100.0,
            format="%.0f",
            label_visibility="visible"
        )


def render_bottom_actions():
    st.markdown("<div style='margin-top: 0.2rem;'></div>", unsafe_allow_html=True)

    btn_left, btn_reset, btn_right = st.columns([5,2,5])

with btn_reset:
    st.button(
        "↺ Reset",
        help="Reset simulator",
        use_container_width=True,
        key="reset_simulator_btn",
        on_click=request_simulator_reset,
    )

    with btn_logout:
        if st.button("⎋", help="Logout", use_container_width=True, key="logout_btn"):
            user = st.session_state.username
            if user in st.session_state.active_users:
                del st.session_state.active_users[user]

            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
