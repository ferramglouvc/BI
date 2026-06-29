import calendar
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from components.login import render_login, validate_session
from components.styles import apply_styles
from components.matrix import render_matrix
from components.filters import render_filters
from components.simulator import (
    init_simulator_context,
    render_simulator,
    render_bottom_actions,
)
from services.loaders import load_data, load_metric_file
from services.aggregations import aggregate_actual_defaults, summarize_metric_subset
from services.calculations import calculate_actual_kpis, calculate_projection
from services.project_leaders import PROJECT_LEADERS

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="KPI Calculator",
    layout="wide"
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
# SALES VIEW
# =====================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

actual_path = DATA_DIR / "kpi_table.csv"
actual_all = load_data(actual_path.stat().st_mtime)

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

title_col, logout_col = st.columns([20, 1])

with title_col:
    st.title("BI Calculator")

with logout_col:
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    if st.button(
        "⎋",
        help="Logout",
        key="logout_header",
    ):
        user = st.session_state.username

        if user in st.session_state.active_users:
            del st.session_state.active_users[user]

        st.session_state.authenticated = False
        st.session_state.username = None

        st.rerun()

yesterday = datetime.now() - timedelta(days=1)
st.caption(f"Data until {yesterday.strftime('%B %d, %Y')}")

# =====================================
# FILTERS
# =====================================

project_leader, salesroom, selected_salesrooms = render_filters(actual_all, PROJECT_LEADERS)

sales_view = st.segmented_control(
    "Sales View",
    ["New Sales", "Upgrades", "Cost Basis"],
    default="Cost Basis"
)

if sales_view == "New Sales":
    df = actual_all[
        (actual_all["SalesRoom"].isin(selected_salesrooms)) &
        (actual_all["Sales Type"].astype(str).str.strip().str.upper() == "N")
    ].copy()

    forecast_df = forecast_new
    budget_df = budget_new

elif sales_view == "Upgrades":
    df = actual_all[
        (actual_all["SalesRoom"].isin(selected_salesrooms)) &
        (actual_all["Sales Type"].astype(str).str.strip().str.upper() == "U")
    ].copy()

    forecast_df = forecast_upg
    budget_df = budget_upg

else:
    df = actual_all[
        actual_all["SalesRoom"].isin(selected_salesrooms)
    ].copy()

    forecast_df = pd.concat([forecast_new, forecast_upg], ignore_index=True)
    budget_df = pd.concat([budget_new, budget_upg], ignore_index=True)
# =====================================
# FILTER DATA
# =====================================

filtered = df[df["SalesRoom"].isin(selected_salesrooms)]
forecast_filtered = forecast_df[forecast_df["SalesRoom"].isin(selected_salesrooms)]
budget_filtered = budget_df[budget_df["SalesRoom"].isin(selected_salesrooms)]

if filtered.empty:
    st.warning("No actual data found")
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

# =====================================
# ACTUAL DEFAULTS
# =====================================

context_key = f"{sales_view}::{project_leader}::{salesroom}"

if len(filtered) > 1:
    actual_arrivals_default, actual_contracts_default, actual_closing_rate_default, actual_avg_price_default = aggregate_actual_defaults(filtered)
else:
    row = filtered.iloc[0]
    actual_arrivals_default = float(row.get("Arrivals", 0))
    actual_contracts_default = float(row.get("Contracts Processable", 0))
    actual_closing_rate_default = float(row.get("Closing Rate", 0))
    if actual_closing_rate_default <= 1:
        actual_closing_rate_default *= 100
    actual_avg_price_default = float(row.get("Average Price", 0))

init_simulator_context(
    context_key,
    {
        "arrivals": actual_arrivals_default,
        "contracts": actual_contracts_default,
        "closing_rate": actual_closing_rate_default,
        "avg_price": actual_avg_price_default,
    }
)

if st.session_state.get("sim_reset_requested"):
    defaults = st.session_state.get("sim_defaults", {})
    if defaults:
        st.session_state["sim_arrivals"] = defaults["arrivals"]
        st.session_state["sim_contracts"] = defaults["contracts"]
        st.session_state["sim_closing_rate"] = defaults["closing_rate"]
        st.session_state["sim_avg_price"] = defaults["avg_price"]

    st.session_state["sim_reset_requested"] = False

# =====================================
# CURRENT SIMULATOR VALUES
# =====================================

arrivals = float(st.session_state["sim_arrivals"])
contracts = float(st.session_state["sim_contracts"])
closing_rate = float(st.session_state["sim_closing_rate"])
avg_price = float(st.session_state["sim_avg_price"])

# =====================================
# ACTUAL CALCULATIONS
# =====================================

actual_metrics = calculate_actual_kpis(arrivals, contracts, closing_rate, avg_price)
qs = actual_metrics["Qs"]
penetration = actual_metrics["Penetration"]
volume = contracts * avg_price
vpg = actual_metrics["VPG"]

# =====================================
# PROJECTION
# =====================================

today = pd.Timestamp.today().normalize()
legend_date = today - pd.Timedelta(days=1)
days_elapsed = legend_date.day
days_in_month = calendar.monthrange(legend_date.year, legend_date.month)[1]
days_remaining = days_in_month - days_elapsed

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

st.markdown("<div class='section-title'>KPI Matrix</div>", unsafe_allow_html=True)
st.caption(
    f"Projection based on {legend_date.strftime('%B %d, %Y')} | {days_remaining} days remaining"
)

matrix_rows = [
    ("Volume", volume, proj_volume, forecast_volume, budget_volume, var_volume_fcst, var_volume_budget, "money"),
    ("Arrivals", arrivals, proj_arrivals, forecast_arrivals, budget_arrivals, var_arrivals_fcst, var_arrivals_budget, "int"),
    ("Contracts", contracts, proj_contracts, forecast_contracts, budget_contracts, var_contracts_fcst, var_contracts_budget, "int"),
    ("Closing Rate", closing_rate, proj_closing_rate, forecast_closing_rate, budget_closing_rate, var_closing_pp_fcst, var_closing_pp_budget, "pct"),
    ("Average Price", avg_price, proj_avg_price, forecast_avg_price, budget_avg_price, var_avg_price_fcst, var_avg_price_budget, "money"),
    ("Qs", qs, proj_qs, forecast_qs, budget_qs, var_qs_fcst, var_qs_budget, "int"),
    ("Penetration", penetration, proj_penetration, forecast_penetration, budget_penetration, var_penetration_pp_fcst, var_penetration_pp_budget, "pct"),
    ("VPG", vpg, proj_vpg, forecast_vpg, budget_vpg, var_vpg_fcst, var_vpg_budget, "money"),
]

render_matrix(matrix_rows, COLORS)

# =====================================
# ACTUALS SIMULATOR
# =====================================

st.markdown("<div style='margin-top: -0.2rem;'></div>", unsafe_allow_html=True)

render_simulator()

# =====================================
# BOTTOM ACTIONS
# =====================================

render_bottom_actions()
