import streamlit as st


# =====================================
# INTERNAL CALCULATIONS
# =====================================

def _calculate_penetration(
    arrivals: float,
    contracts: float,
    closing_rate: float,
) -> float:
    """Return Penetration % from Arrivals, Contracts and Closing Rate %."""

    if arrivals <= 0 or closing_rate <= 0:
        return 0.0

    qs = contracts / (closing_rate / 100)
    return (qs / arrivals) * 100


def _calculate_contracts(
    arrivals: float,
    penetration: float,
    closing_rate: float,
) -> float:
    """Return Contracts from Arrivals, Penetration % and Closing Rate %."""

    if arrivals <= 0 or penetration < 0 or closing_rate < 0:
        return 0.0

    qs = arrivals * (penetration / 100)
    return qs * (closing_rate / 100)


# =====================================
# CALLBACKS
# =====================================

def _sync_from_penetration() -> None:
    arrivals = float(st.session_state.get("sim_arrivals", 0.0))
    penetration = float(st.session_state.get("sim_penetration", 0.0))
    closing_rate = float(st.session_state.get("sim_closing_rate", 0.0))

    st.session_state["sim_contracts"] = _calculate_contracts(
        arrivals,
        penetration,
        closing_rate,
    )


def _sync_from_contracts() -> None:
    arrivals = float(st.session_state.get("sim_arrivals", 0.0))
    contracts = float(st.session_state.get("sim_contracts", 0.0))
    closing_rate = float(st.session_state.get("sim_closing_rate", 0.0))

    st.session_state["sim_penetration"] = _calculate_penetration(
        arrivals,
        contracts,
        closing_rate,
    )


def _sync_from_closing_rate() -> None:
    arrivals = float(st.session_state.get("sim_arrivals", 0.0))
    penetration = float(st.session_state.get("sim_penetration", 0.0))
    closing_rate = float(st.session_state.get("sim_closing_rate", 0.0))

    st.session_state["sim_contracts"] = _calculate_contracts(
        arrivals,
        penetration,
        closing_rate,
    )


# =====================================
# INITIALIZATION
# =====================================

def init_simulator_context(context_key, defaults):
    """Initialize simulator state when the filter context changes."""

    arrivals = float(defaults.get("arrivals", 0.0) or 0.0)
    contracts = float(defaults.get("contracts", 0.0) or 0.0)
    closing_rate = float(defaults.get("closing_rate", 0.0) or 0.0)
    avg_price = float(defaults.get("avg_price", 0.0) or 0.0)

    penetration = float(
        defaults.get(
            "penetration",
            _calculate_penetration(
                arrivals,
                contracts,
                closing_rate,
            ),
        )
        or 0.0
    )

    normalized_defaults = {
        "arrivals": arrivals,
        "penetration": penetration,
        "contracts": contracts,
        "closing_rate": closing_rate,
        "avg_price": avg_price,
    }

    required_keys = {
        "sim_arrivals",
        "sim_penetration",
        "sim_contracts",
        "sim_closing_rate",
        "sim_avg_price",
    }

    context_changed = (
        st.session_state.get("sim_context") != context_key
    )

    state_incomplete = any(
        key not in st.session_state
        for key in required_keys
    )

    if context_changed or state_incomplete:
        st.session_state["sim_defaults"] = normalized_defaults.copy()
        st.session_state["sim_arrivals"] = arrivals
        st.session_state["sim_penetration"] = penetration
        st.session_state["sim_contracts"] = contracts
        st.session_state["sim_closing_rate"] = closing_rate
        st.session_state["sim_avg_price"] = avg_price
        st.session_state["sim_context"] = context_key


# =====================================
# RESET
# =====================================

def request_simulator_reset() -> None:
    st.session_state["sim_reset_requested"] = True


# =====================================
# RENDER
# =====================================

def render_simulator() -> None:
    st.markdown(
        "<div class='section-title' style='margin-top:0rem;"
        "margin-bottom:0rem;'>Actuals Simulator</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='margin-top:-0.75rem;'></div>",
        unsafe_allow_html=True,
    )

    row1_col1, row1_col2 = st.columns(2, gap="small")
    row2_col1, row2_col2 = st.columns(2, gap="small")

    with row1_col1:
        st.number_input(
            "Penetration %",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            key="sim_penetration",
            on_change=_sync_from_penetration,
            label_visibility="visible",
        )

    with row1_col2:
        st.number_input(
            "Contracts",
            min_value=0.0,
            step=1.0,
            format="%.0f",
            key="sim_contracts",
            on_change=_sync_from_contracts,
            label_visibility="visible",
        )

    with row2_col1:
        st.number_input(
            "Closing Rate %",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            key="sim_closing_rate",
            on_change=_sync_from_closing_rate,
            label_visibility="visible",
        )

    with row2_col2:
        st.number_input(
            "Average Price ($)",
            min_value=0.0,
            step=100.0,
            format="%.0f",
            key="sim_avg_price",
            label_visibility="visible",
        )


def render_bottom_actions() -> None:
    st.markdown(
        "<div style='margin-top:0.3rem;'></div>",
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([5, 2, 5])

    with center:
        st.button(
            "↺",
            help="Reset simulator",
            key="reset_simulator_btn",
            on_click=request_simulator_reset,
            width="stretch",
        )
