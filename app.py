from datetime import datetime, timedelta
import calendar
import uuid

import pandas as pd
import streamlit as st

from components.styles import apply_styles
from components.matrix import render_matrix
from services.loaders import load_data, load_metric_file
from services.aggregations import aggregate_actual_defaults, aggregate_metric_defaults
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
# SIMPLE LOGIN
# =====================================

USERS = {
    "admin": "uvc2026",
    "erick": "kpi2026",
}

# =====================================
# SESSION STATE
# =====================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "active_users" not in st.session_state:
    st.session_state.active_users = {}

# =====================================
# LOGIN
# =====================================

if not st.session_state.authenticated:

    st.title("Login")

    with st.form("login_form"):
        user = st.text_input("User")
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if user in USERS and pwd == USERS[user]:
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

# =====================================
# VALIDATE ACTIVE SESSION
# =====================================

if st.session_state.username:
    active_id = st.session_state.active_users.get(st.session_state.username)
    if active_id != st.session_state.session_id:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.error("Your session was replaced by another login.")
        st.stop()

# =====================================
# LOGOUT BUTTON
# =====================================

logout_col1, logout_col2 = st.columns([8, 1])

with logout_col2:
    if st.button("Logout"):
        user = st.session_state.username
        if user in st.session_state.active_users:
            del st.session_state.active_users[user]
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# =====================================
# PATH / DATA
# =====================================

df = load_data()
forecast_df = load_metric_file("May_Forecast.csv")
budget_df = load_metric_file("June_Budget.csv")  # cambia a "Jun_Budget.csv" si ese es el nombre real

# =====================================
# TITLE / LEGEND
# =====================================

st.title("Calculadora BI")

yesterday = datetime.now() - timedelta(days=1)
st.caption(f"Data until {yesterday.strftime('%B %d, %Y')}")

# =====================================
# HELPERS
# =====================================

def normalize_percent(value):
    if pd.isna(value):
        return 0.0
    value = float(value)
    return value * 100 if value <= 1 else value

def input_card(title, value, step, fmt="%d"):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        return st.number_input(
            title,
            value=value,
            step=step,
            format=fmt,
            label_visibility="collapsed"
        )

# =====================================
# PROJECT LEADER / SALESROOM FILTER
# =====================================

all_salesrooms = sorted(
    df["SalesRoom"].dropna().astype(str).unique().tolist(),
    key=str.lower
)

leader_names = sorted(
    [name for name in PROJECT_LEADERS.keys() if name != "ALL"],
    key=str.lower
)

leader_options = ["ALL"] + leader_names

project_leader = st.selectbox(
    "Select Project Leader",
    leader_options
)

if project_leader == "ALL":
    leader_salesrooms = all_salesrooms
else:
    leader_salesrooms = sorted(PROJECT_LEADERS[project_leader], key=str.lower)

salesroom_options = ["ALL"] + leader_salesrooms

salesroom = st.selectbox(
    "Select SalesRoom",
    salesroom_options
)

if salesroom == "ALL":
    selected_salesrooms = leader_salesrooms
else:
    selected_salesrooms = [salesroom]

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

if salesroom == "ALL":
    actual_arrivals, actual_contracts, actual_closing_rate, actual_avg_price = aggregate_actual_defaults(filtered)
    forecast_agg = aggregate_metric_defaults(forecast_filtered, selected_salesrooms)
    budget_agg = aggregate_metric_defaults(budget_filtered, selected_salesrooms)
else:
    row = filtered.iloc[0]
    forecast_row = forecast_filtered.iloc[0]
    budget_row = budget_filtered.iloc[0]

    actual_arrivals = int(round(float(row["Arrivals"])))
    actual_contracts = int(round(float(row["Contracts Processable"])))
    actual_closing_rate = float(row["Closing Rate"]) * 100 if float(row["Closing Rate"]) <= 1 else float(row["Closing Rate"])
    actual_avg_price = int(round(float(row["Average Price"])))

# =====================================
# ACTUAL INPUTS
# =====================================

st.markdown("<div class='section-title'>Actuals KPIs</div>", unsafe_allow_html=True)

if salesroom == "ALL":
    st.caption(f"Consolidated view for {project_leader} | {len(selected_salesrooms)} salesrooms")

i1, i2, i3, i4 = st.columns(4, gap="small")

with i1:
    arrivals = input_card("Arrivals", int(round(float(actual_arrivals))), step=1, fmt="%d")

with i2:
    contracts = input_card("Contracts", int(round(float(actual_contracts))), step=1, fmt="%d")

with i3:
    closing_rate = input_card("Closing Rate %", float(actual_closing_rate), step=0.1, fmt="%.1f")

with i4:
    avg_price = input_card("Average Price ($)", int(round(float(actual_avg_price))), step=100, fmt="%d")

# =====================================
# ACTUAL CALCULATIONS
# =====================================

qs = contracts / (closing_rate / 100) if closing_rate else 0
penetration = (qs / arrivals * 100) if arrivals else 0
volume = contracts * avg_price
vpg = volume / qs if qs else 0

# =====================================
# FORECAST EOM
# =====================================

today = pd.Timestamp.today().normalize()
legend_date = today - pd.Timedelta(days=1)

days_elapsed = legend_date.day
days_in_month = calendar.monthrange(legend_date.year, legend_date.month)[1]
days_remaining = days_in_month - days_elapsed

def project_mtd(value):
    return (value / days_elapsed) * days_in_month if days_elapsed else 0

proj_arrivals = project_mtd(arrivals)
proj_contracts = project_mtd(contracts)
proj_qs = project_mtd(qs)
proj_volume = project_mtd(volume)

proj_penetration = (proj_qs / proj_arrivals * 100) if proj_arrivals else 0
proj_closing_rate = (proj_contracts / proj_qs * 100) if proj_qs else 0
proj_vpg = (proj_volume / proj_qs) if proj_qs else 0
proj_avg_price = (proj_volume / proj_contracts) if proj_contracts else 0

# =====================================
# FORECAST TARGETS
# =====================================

if salesroom == "ALL":
    forecast_arrivals = forecast_agg["Arrivals"]
    forecast_penetration = forecast_agg["Penetration"]
    forecast_qs = forecast_agg["Qs"]
    forecast_contracts = forecast_agg["Contracts"]
    forecast_avg_price = forecast_agg["Average Price"]
    forecast_closing_rate = forecast_agg["Closing Rate"]
    forecast_vpg = forecast_agg["VPG"]
    forecast_volume = forecast_agg["Volume"]
else:
    forecast_arrivals = float(forecast_row.get("Arrivals", 0))

    forecast_penetration = float(forecast_row.get("Penetration", 0))
    if forecast_penetration <= 1:
        forecast_penetration *= 100

    forecast_qs = float(forecast_row.get("Qs", 0))
    forecast_contracts = float(forecast_row.get("Contracts", 0))
    forecast_avg_price = float(forecast_row.get("Average Price", 0))

    forecast_closing_rate = float(forecast_row.get("Closing Rate", 0))
    if forecast_closing_rate <= 1:
        forecast_closing_rate *= 100

    forecast_vpg = float(forecast_row.get("VPG", 0))
    forecast_volume = float(forecast_row.get("Volume", 0))

# =====================================
# BUDGET TARGETS
# =====================================

if salesroom == "ALL":
    budget_arrivals = budget_agg["Arrivals"]
    budget_penetration = budget_agg["Penetration"]
    budget_qs = budget_agg["Qs"]
    budget_contracts = budget_agg["Contracts"]
    budget_avg_price = budget_agg["Average Price"]
    budget_closing_rate = budget_agg["Closing Rate"]
    budget_vpg = budget_agg["VPG"]
    budget_volume = budget_agg["Volume"]
else:
    budget_arrivals = float(budget_row.get("Arrivals", 0))

    budget_penetration = float(budget_row.get("Penetration", 0))
    if budget_penetration <= 1:
        budget_penetration *= 100

    budget_qs = float(budget_row.get("Qs", 0))
    budget_contracts = float(budget_row.get("Contracts", 0))
    budget_avg_price = float(budget_row.get("Average Price", 0))

    budget_closing_rate = float(budget_row.get("Closing Rate", 0))
    if budget_closing_rate <= 1:
        budget_closing_rate *= 100

    budget_vpg = float(budget_row.get("VPG", 0))
    budget_volume = float(budget_row.get("Volume", 0))

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
    ("Arrivals", arrivals, proj_arrivals, forecast_arrivals, budget_arrivals, var_arrivals_fcst, var_arrivals_budget, "int"),
    ("Contracts", contracts, proj_contracts, forecast_contracts, budget_contracts, var_contracts_fcst, var_contracts_budget, "int"),
    ("Closing Rate", closing_rate, proj_closing_rate, forecast_closing_rate, budget_closing_rate, var_closing_pp_fcst, var_closing_pp_budget, "pct"),
    ("Average Price", avg_price, proj_avg_price, forecast_avg_price, budget_avg_price, var_avg_price_fcst, var_avg_price_budget, "money"),
    ("Qs", qs, proj_qs, forecast_qs, budget_qs, var_qs_fcst, var_qs_budget, "int"),
    ("Penetration", penetration, proj_penetration, forecast_penetration, budget_penetration, var_penetration_pp_fcst, var_penetration_pp_budget, "pct"),
    ("VPG", vpg, proj_vpg, forecast_vpg, budget_vpg, var_vpg_fcst, var_vpg_budget, "money"),
    ("Volume", volume, proj_volume, forecast_volume, budget_volume, var_volume_fcst, var_volume_budget, "money"),
]

render_matrix(matrix_rows, COLORS)
