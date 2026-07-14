import calendar
from pathlib import Path

import pandas as pd
import streamlit as st

from components.filters import render_filters
from components.login import render_login, validate_session
from components.matrix import render_matrix
from components.simulator import (
    init_simulator_context,
    render_bottom_actions,
    render_simulator,
)
from components.styles import apply_styles
from services.aggregations import (
    aggregate_actual_defaults,
    summarize_metric_subset,
)
from services.calculations import (
    calculate_actual_kpis,
    calculate_projection,
)
from services.loaders import load_data, load_metric_file
from services.project_leaders import PROJECT_LEADERS
from utils.dates import get_data_date


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="KPI Calculator",
    layout="wide",
)

COLORS = {
    "bg": "#0e1117",
    "card_bg": "rgba(255,255,255,0.03)",
    "text": "#f5f7fa",
    "muted": "rgba(245,247,250,0.70)",
    "border": "rgba(255,255,255,0.12)",
    "header_bg": "#0e1117",
    "sticky_bg": "#0e1117",
    "positive": "#28a745",
    "negative": "#dc3545",
}

apply_styles(COLORS)


# =====================================
# AUTH
# =====================================

USERS = {
    "admin": "uvc2026",
    "erick": "kpi2026",
}

render_login(USERS)
validate_session()


# =====================================
# LOAD DATA
# =====================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

actual_path = DATA_DIR / "kpi_table.csv"
actual_all = load_data(actual_path.stat().st_mtime)

# Normalize Power BI-style headers such as [SalesRoom].
actual_all.columns = (
    actual_all.columns
    .astype(str)
    .str.replace("[", "", regex=False)
    .str.replace("]", "", regex=False)
    .str.strip()
)

required_actual_columns = {
    "SalesRoom",
    "Sales Type",
    "Membership Type",
    "Average Price",
    "Closing Rate",
    "Arrivals",
    "Contracts Processable",
}

missing_actual_columns = sorted(
    required_actual_columns.difference(actual_all.columns)
)

if missing_actual_columns:
    st.error(
        "kpi_table.csv is missing required columns: "
        + ", ".join(missing_actual_columns)
    )
    st.code("\n".join(str(column) for column in actual_all.columns))
    st.stop()

forecast_new = load_metric_file(
    "forecast_new.csv",
    (DATA_DIR / "forecast_new.csv").stat().st_mtime,
)

forecast_upg = load_metric_file(
    "forecast_upgrades.csv",
    (DATA_DIR / "forecast_upgrades.csv").stat().st_mtime,
)

budget_new = load_metric_file(
    "budget_new.csv",
    (DATA_DIR / "budget_new.csv").stat().st_mtime,
)

budget_upg = load_metric_file(
    "budget_upgrades.csv",
    (DATA_DIR / "budget_upgrades.csv").stat().st_mtime,
)


# =====================================
# HEADER
# =====================================

st.title("BI Calculator")

data_date = get_data_date()

st.caption(
    f"Data until {data_date.strftime('%B %d, %Y')}"
)


# =====================================
# PRIMARY FILTERS
# =====================================

project_leader, salesroom, selected_salesrooms = render_filters(
    actual_all,
    PROJECT_LEADERS,
)

sales_view = st.segmented_control(
    "Sales View",
    ["New Sales", "Upgrades", "Cost Basis"],
    default="Cost Basis",
    key="sales_view",
)


# =====================================
# APPLY SALES VIEW
# =====================================

sales_type_series = (
    actual_all["Sales Type"]
    .astype(str)
    .str.strip()
    .str.upper()
)

if sales_view == "New Sales":
    df = actual_all[
        actual_all["SalesRoom"].isin(selected_salesrooms)
        & sales_type_series.eq("N")
    ].copy()

    forecast_df = forecast_new
    budget_df = budget_new

elif sales_view == "Upgrades":
    df = actual_all[
        actual_all["SalesRoom"].isin(selected_salesrooms)
        & sales_type_series.eq("U")
    ].copy()

    forecast_df = forecast_upg
    budget_df = budget_upg

else:
    df = actual_all[
        actual_all["SalesRoom"].isin(selected_salesrooms)
    ].copy()

    forecast_df = pd.concat(
        [forecast_new, forecast_upg],
        ignore_index=True,
    )

    budget_df = pd.concat(
        [budget_new, budget_upg],
        ignore_index=True,
    )

if df.empty:
    st.warning("No actual data found for the selected Sales View.")
    st.stop()


# =====================================
# MEMBERSHIP TYPE FILTER
# =====================================

membership_series = (
    df["Membership Type"]
    .astype("string")
    .str.strip()
)

df["Membership Type"] = membership_series

membership_values = sorted(
    value
    for value in membership_series.dropna().unique().tolist()
    if value
)

membership_type = st.selectbox(
    "Membership Type",
    options=["All", *membership_values],
    index=0,
    key=(
        f"membership_filter::"
        f"{sales_view}::"
        f"{project_leader}::"
        f"{salesroom}"
    ),
)

if membership_type != "All":
    df = df[
        df["Membership Type"].eq(membership_type)
    ].copy()

    st.caption(
        "Forecast and Budget remain at SalesRoom level because "
        "the target files do not include Membership Type."
    )


# =====================================
# FILTER TARGET DATA
# =====================================

filtered = df[
    df["SalesRoom"].isin(selected_salesrooms)
].copy()

forecast_filtered = forecast_df[
    forecast_df["SalesRoom"].isin(selected_salesrooms)
].copy()

budget_filtered = budget_df[
    budget_df["SalesRoom"].isin(selected_salesrooms)
].copy()

if filtered.empty:
    st.warning("No actual data found for the selected filters.")
    st.stop()

if forecast_filtered.empty:
    st.warning("No forecast data found")
    st.stop()

if budget_filtered.empty:
    st.warning("No budget data found")
    st.stop()


# =====================================
# ACTUAL DEFAULTS
# =====================================

context_key = (
    f"{sales_view}::"
    f"{project_leader}::"
    f"{salesroom}::"
    f"{membership_type}"
)

if len(filtered) > 1:
    (
        actual_arrivals_default,
        actual_contracts_default,
        actual_closing_rate_default,
        actual_avg_price_default,
    ) = aggregate_actual_defaults(filtered)

else:
    row = filtered.iloc[0]

    actual_arrivals_default = float(
        row.get("Arrivals", 0) or 0
    )

    actual_contracts_default = float(
        row.get("Contracts Processable", 0) or 0
    )

    # Source stores Closing Rate as a ratio:
    # 0.40 = 40%, 1.50 = 150%.
    actual_closing_rate_default = (
        float(row.get("Closing Rate", 0) or 0) * 100
    )

    actual_avg_price_default = float(
        row.get("Average Price", 0) or 0
    )

actual_qs_default = (
    actual_contracts_default
    / (actual_closing_rate_default / 100)
    if actual_closing_rate_default
    else 0.0
)

actual_penetration_default = (
    actual_qs_default / actual_arrivals_default * 100
    if actual_arrivals_default
    else 0.0
)

init_simulator_context(
    context_key,
    {
        "arrivals": actual_arrivals_default,
        "penetration": actual_penetration_default,
        "contracts": actual_contracts_default,
        "closing_rate": actual_closing_rate_default,
        "avg_price": actual_avg_price_default,
    },
)


# =====================================
# RESET SIMULATOR
# =====================================

if st.session_state.get("sim_reset_requested"):
    defaults = st.session_state.get("sim_defaults", {})

    if defaults:
        st.session_state["sim_arrivals"] = float(
            defaults.get("arrivals", actual_arrivals_default)
        )
        st.session_state["sim_penetration"] = float(
            defaults.get("penetration", actual_penetration_default)
        )
        st.session_state["sim_contracts"] = float(
            defaults.get("contracts", actual_contracts_default)
        )
        st.session_state["sim_closing_rate"] = float(
            defaults.get("closing_rate", actual_closing_rate_default)
        )
        st.session_state["sim_avg_price"] = float(
            defaults.get("avg_price", actual_avg_price_default)
        )

    st.session_state["sim_reset_requested"] = False


# =====================================
# CURRENT SIMULATOR VALUES
# =====================================

arrivals = float(
    st.session_state.get("sim_arrivals", actual_arrivals_default)
)

contracts = float(
    st.session_state.get("sim_contracts", actual_contracts_default)
)

closing_rate = float(
    st.session_state.get(
        "sim_closing_rate",
        actual_closing_rate_default,
    )
)

avg_price = float(
    st.session_state.get("sim_avg_price", actual_avg_price_default)
)


# =====================================
# ACTUAL CALCULATIONS
# =====================================

actual_metrics = calculate_actual_kpis(
    arrivals,
    contracts,
    closing_rate,
    avg_price,
)

qs = actual_metrics["Qs"]
penetration = actual_metrics["Penetration"]
volume = contracts * avg_price
vpg = actual_metrics["VPG"]

# The simulator is rendered later in the script, so updating its
# penetration state here is safe and keeps the visible value aligned.
st.session_state["sim_penetration"] = float(penetration)


# =====================================
# PROJECTION
# =====================================

days_elapsed = data_date.day
days_in_month = calendar.monthrange(
    data_date.year,
    data_date.month,
)[1]
days_remaining = max(days_in_month - data_date.day, 0)

projection = calculate_projection(
    arrivals=arrivals,
    contracts=contracts,
    qs=qs,
    volume=volume,
    days_elapsed=days_elapsed,
    days_in_month=days_in_month,
)

proj_arrivals = projection["Arrivals"]
proj_contracts = projection["Contracts"]
proj_qs = projection["Qs"]
proj_volume = projection["Volume"]
proj_penetration = projection["Penetration"]
proj_closing_rate = projection["Closing Rate"]
proj_vpg = projection["VPG"]
proj_avg_price = projection["Average Price"]


# =====================================
# TARGETS
# =====================================

forecast_summary = summarize_metric_subset(forecast_filtered)
budget_summary = summarize_metric_subset(budget_filtered)

forecast_arrivals = forecast_summary["Arrivals"]
forecast_penetration = forecast_summary["Penetration"]
forecast_qs = forecast_summary["Qs"]
forecast_contracts = forecast_summary["Contracts"]
forecast_avg_price = forecast_summary["Average Price"]
forecast_closing_rate = forecast_summary["Closing Rate"]
forecast_vpg = forecast_summary["VPG"]
forecast_volume = forecast_summary["Volume"]

budget_arrivals = budget_summary["Arrivals"]
budget_penetration = budget_summary["Penetration"]
budget_qs = budget_summary["Qs"]
budget_contracts = budget_summary["Contracts"]
budget_avg_price = budget_summary["Average Price"]
budget_closing_rate = budget_summary["Closing Rate"]
budget_vpg = budget_summary["VPG"]
budget_volume = budget_summary["Volume"]


# =====================================
# VARIANCES
# =====================================

var_arrivals_fcst = proj_arrivals - forecast_arrivals
var_contracts_fcst = proj_contracts - forecast_contracts
var_qs_fcst = proj_qs - forecast_qs
var_volume_fcst = proj_volume - forecast_volume
var_penetration_pp_fcst = proj_penetration - forecast_penetration
var_closing_pp_fcst = proj_closing_rate - forecast_closing_rate
var_vpg_fcst = proj_vpg - forecast_vpg
var_avg_price_fcst = proj_avg_price - forecast_avg_price

var_arrivals_budget = proj_arrivals - budget_arrivals
var_contracts_budget = proj_contracts - budget_contracts
var_qs_budget = proj_qs - budget_qs
var_volume_budget = proj_volume - budget_volume
var_penetration_pp_budget = proj_penetration - budget_penetration
var_closing_pp_budget = proj_closing_rate - budget_closing_rate
var_vpg_budget = proj_vpg - budget_vpg
var_avg_price_budget = proj_avg_price - budget_avg_price


# =====================================
# MATRIX
# =====================================

st.markdown(
    "<div class='section-title'>KPI Matrix</div>",
    unsafe_allow_html=True,
)

st.caption(
    f"Projection based on {data_date.strftime('%B %d, %Y')} | "
    f"{days_remaining} days remaining"
)

matrix_rows = [
    (
        "Volume",
        volume,
        proj_volume,
        forecast_volume,
        budget_volume,
        var_volume_fcst,
        var_volume_budget,
        "money",
    ),
    (
        "Arrivals",
        arrivals,
        proj_arrivals,
        forecast_arrivals,
        budget_arrivals,
        var_arrivals_fcst,
        var_arrivals_budget,
        "int",
    ),
    (
        "Contracts",
        contracts,
        proj_contracts,
        forecast_contracts,
        budget_contracts,
        var_contracts_fcst,
        var_contracts_budget,
        "int",
    ),
    (
        "Closing Rate",
        closing_rate,
        proj_closing_rate,
        forecast_closing_rate,
        budget_closing_rate,
        var_closing_pp_fcst,
        var_closing_pp_budget,
        "pct",
    ),
    (
        "Average Price",
        avg_price,
        proj_avg_price,
        forecast_avg_price,
        budget_avg_price,
        var_avg_price_fcst,
        var_avg_price_budget,
        "money",
    ),
    (
        "Qs",
        qs,
        proj_qs,
        forecast_qs,
        budget_qs,
        var_qs_fcst,
        var_qs_budget,
        "int",
    ),
    (
        "Penetration",
        penetration,
        proj_penetration,
        forecast_penetration,
        budget_penetration,
        var_penetration_pp_fcst,
        var_penetration_pp_budget,
        "pct",
    ),
    (
        "VPG",
        vpg,
        proj_vpg,
        forecast_vpg,
        budget_vpg,
        var_vpg_fcst,
        var_vpg_budget,
        "money",
    ),
]

render_matrix(matrix_rows, COLORS)


# =====================================
# ACTUALS SIMULATOR
# =====================================

st.markdown(
    "<div style='margin-top:-0.2rem;'></div>",
    unsafe_allow_html=True,
)

render_simulator()


# =====================================
# BOTTOM ACTIONS
# =====================================

render_bottom_actions()
