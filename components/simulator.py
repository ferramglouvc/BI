import streamlit as st


# =====================================
# INTERNAL CALCULATIONS
# =====================================

def _calculate_penetration(
    arrivals: float,
    contracts: float,
    closing_rate: float,
) -> float:
    """
    Calculate Penetration % from:
    Contracts -> Qs -> Penetration.
    """

    if arrivals <= 0 or closing_rate <= 0:
        return 0.0

    qs = contracts / (closing_rate / 100)

    return (qs / arrivals) * 100


def _calculate_contracts(
    arrivals: float,
    penetration: float,
    closing_rate: float,
) -> float:
    """
    Calculate Contracts from:
    Arrivals -> Penetration -> Qs -> Contracts.
    """

    if arrivals <= 0:
        return 0.0

    qs = arrivals * (penetration / 100)

    return qs * (closing_rate / 100)


# =====================================
# WIDGET CALLBACKS
# =====================================

def _sync_from_penetration() -> None:
    """
    When Penetration changes:
    - Arrivals stays fixed
    - Qs changes
    - Contracts changes
    """

    arrivals = float(
        st.session_state.get("sim_arrivals", 0)
    )

    penetration = float(
        st.session_state.get("sim_penetration", 0)
    )

    closing_rate = float(
        st.session_state.get("sim_closing_rate", 0)
    )

    st.session_state["sim_contracts"] = _calculate_contracts(
        arrivals=arrivals,
        penetration=penetration,
        closing_rate=closing_rate,
    )


def _sync_from_closing_rate() -> None:
    """
    When Closing Rate changes:
    - Penetration stays fixed
    - Qs stays determined by Penetration
    - Contracts changes
    """

    arrivals = float(
        st.session_state.get("sim_arrivals", 0)
    )

    penetration = float(
        st.session_state.get("sim_penetration", 0)
    )

    closing_rate = float(
        st.session_state.get("sim_closing_rate", 0)
    )

    st.session_state["sim_contracts"] = _calculate_contracts(
        arrivals=arrivals,
        penetration=penetration,
        closing_rate=closing_rate,
    )


def _sync_from_contracts() -> None:
    """
    When Contracts changes:
    - Closing Rate stays fixed
    - Qs changes
    - Penetration changes
    """

    arrivals = float(
        st.session_state.get("sim_arrivals", 0)
    )

    contracts = float(
        st.session_state.get("sim_contracts", 0)
    )

    closing_rate = float(
        st.session_state.get("sim_closing_rate", 0)
    )

    st.session_state["sim_penetration"] = _calculate_penetration(
        arrivals=arrivals,
        contracts=contracts,
        closing_rate=closing_rate,
    )


# =====================================
# INITIALIZE SIMULATOR
# =====================================

def init_simulator_context(
    context_key,
    defaults,
):
    """
    Initialize the simulator whenever Sales View,
    Project Leader, SalesRoom, or another context changes.
    """

    arrivals = float(
        defaults.get("arrivals", 0)
    )

    contracts = float(
        defaults.get("contracts", 0)
    )

    closing_rate = float(
        defaults.get("closing_rate", 0)
    )

    avg_price = float(
        defaults.get("avg_price", 0)
    )

    # Calculate the initial Penetration from the existing data.
    penetration = _calculate_penetration(
        arrivals=arrivals,
        contracts=contracts,
        closing_rate=closing_rate,
    )

    normalized_defaults = {
        "arrivals": arrivals,
        "penetration": penetration,
        "contracts": contracts,
        "closing_rate": closing_rate,
        "avg_price": avg_price,
    }

    required_state_keys = [
        "sim_arrivals",
        "sim_penetration",
        "sim_contracts",
        "sim_closing_rate",
        "sim_avg_price",
    ]

    context_changed = (
        st.session_state.get("sim_context")
        != context_key
    )

    state_incomplete = any(
        key not in st.session_state
        for key in required_state_keys
    )

    if context_changed or state_incomplete:
        st.session_state["sim_defaults"] = (
            normalized_defaults.copy()
        )

        st.session_state["sim_arrivals"] = arrivals

        st.session_state["sim_penetration"] = (
            penetration
        )

        st.session_state["sim_contracts"] = (
            contracts
        )

        st.session_state["sim_closing_rate"] = (
            closing_rate
        )

        st.session_state["sim_avg_price"] = (
            avg_price
        )

        st.session_state["sim_context"] = (
            context_key
        )


# =====================================
# RESET
# =====================================

def request_simulator_reset() -> None:
    st.session_state["sim_reset_requested"] = True


# =====================================
# RENDER SIMULATOR
# =====================================

def render_simulator() -> None:
    st.markdown(
        """
        <div
            class="section-title"
            style="margin-top:0rem; margin-bottom:0rem;"
        >
            Actuals Simulator
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='margin-top:-0.75rem;'></div>",
        unsafe_allow_html=True,
    )

    row1_col1, row1_col2 = st.columns(
        2,
        gap="small",
    )

    row2_col1, row2_col2 = st.columns(
        2,
        gap="small",
    )

    # =================================
    # PENETRATION
    # Replaces Arrivals as visible input
    # =================================

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

    # =================================
    # CONTRACTS
    # =================================

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

    # =================================
    # CLOSING RATE
    # =================================

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

    # =================================
    # AVERAGE PRICE
    # =================================

    with row2_col2:
        st.number_input(
            "Average Price ($)",
            min_value=0.0,
            step=100.0,
            format="%.0f",
            key="sim_avg_price",
            label_visibility="visible",
        )


# =====================================
# BOTTOM ACTIONS
# =====================================

def render_bottom_actions() -> None:
    st.markdown(
        "<div style='margin-top:0.3rem;'></div>",
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(
        [5, 2, 5]
    )

    with center:
        st.button(
            "↺",
            help="Reset simulator",
            key="reset_simulator_btn",
            on_click=request_simulator_reset,
            use_container_width=True,
        )
