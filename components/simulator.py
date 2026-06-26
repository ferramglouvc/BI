import streamlit as st
from streamlit_js_eval import streamlit_js_eval


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


def _render_input(col, label, key, value, step, fmt):
    with col:
        st.number_input(
            label,
            key=key,
            value=float(value),
            step=step,
            format=fmt,
            label_visibility="visible",
        )


def render_simulator():
    st.markdown("<div class='section-title'>Actuals Simulator</div>", unsafe_allow_html=True)
    st.markdown("<div class='simulator-wrap'>", unsafe_allow_html=True)

    screen_width = streamlit_js_eval(
        js_expressions="window.innerWidth",
        want_output=True,
        key="WIDTH",
    )

    if screen_width is None:
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    if screen_width < 768:
        row1_col1, row1_col2 = st.columns(2, gap="small")
        row2_col1, row2_col2 = st.columns(2, gap="small")

        _render_input(
            row1_col1, "Arrivals", "sim_arrivals",
            st.session_state["sim_arrivals"], 1.0, "%.0f"
        )
        _render_input(
            row1_col2, "Contracts", "sim_contracts",
            st.session_state["sim_contracts"], 1.0, "%.0f"
        )
        _render_input(
            row2_col1, "Closing Rate %", "sim_closing_rate",
            st.session_state["sim_closing_rate"], 0.1, "%.1f"
        )
        _render_input(
            row2_col2, "Average Price ($)", "sim_avg_price",
            st.session_state["sim_avg_price"], 100.0, "%.0f"
        )
    else:
        c1, c2, c3, c4 = st.columns(4, gap="small")

        _render_input(c1, "Arrivals", "sim_arrivals", st.session_state["sim_arrivals"], 1.0, "%.0f")
        _render_input(c2, "Contracts", "sim_contracts", st.session_state["sim_contracts"], 1.0, "%.0f")
        _render_input(c3, "Closing Rate %", "sim_closing_rate", st.session_state["sim_closing_rate"], 0.1, "%.1f")
        _render_input(c4, "Average Price ($)", "sim_avg_price", st.session_state["sim_avg_price"], 100.0, "%.0f")

    st.markdown("</div>", unsafe_allow_html=True)


def render_bottom_actions():
    st.markdown("<div style='margin-top: 0.2rem;'></div>", unsafe_allow_html=True)

    btn_left, btn_reset, btn_logout, btn_right = st.columns([5, 1, 1, 5])

    with btn_reset:
        st.button(
            "↺",
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
