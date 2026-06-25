import html
import pathlib
from datetime import datetime, timedelta
import calendar
import uuid

import pandas as pd
import streamlit as st

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="KPI Calculator",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: #0e1117;
        color: #f5f7fa;
    }

    [data-testid="stHeader"] {
        background: #0e1117;
    }

    [data-testid="stSidebar"] {
        background: #0e1117;
    }

    .stApp {
        background: #0e1117;
        color: #f5f7fa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# SIMPLE LOGIN
# =====================================

USERS = {
    "admin": "uvc2026",
    "erick": "kpi2026",
}

PROJECT_LEADERS = {
    "ALL": [],
    "Angel Marin": ["SUDLR", "SECCC", "SERPC"],
    "Claudio Balderrama": ["SUDIX"],
    "Cristina Ortiz": ["DRBMI", "SEBMI"],
    "Florin Ignat": ["DRJRC", "SEMRC", "DRENA", "SEPDC", "BRERG"],
    "Gabriel Prado": ["SETPC", "DRMPC", "DRFPC", "BREPC", "DRCTG", "DRECC", "DROPC", "DREPE", "DRELR", "PUJIF"],
    "Guillermo Mejia": ["DDPBP"],
    "Ivan Brambila": ["DRVPV", "SEVPV", "SUNPV"],
    "Ladislao Oquendo": ["SECHU", "DREHU"],
    "Ricardo Arriola": ["BRCSL", "DRELC", "SEPLC", "ZOCDM"],
    "Juan Manuel Marquez": ["PVRIF"],
    "Alain Chalut": ["DRMZT"],
    "Rodolfo Osoyo": ["SEARM", "DRETU", "DRCZM"],
    "Chad Knowles": ["ZOMSL", "SEWMB", "SMBSL", "SEAUA"],
    "Victor Camarillo": ["DREPM", "SEPBC", "SEVCU", "NOECU", "DREVC", "BRECU", "CANIF", "SEIIM"],
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
# THEME HELPERS
# =====================================

def theme_colors():
    return {
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

COLORS = theme_colors()

# =====================================
# STYLES
# =====================================

st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 1rem;
    }}

    div[data-baseweb="input"] input {{
        font-size: 16px!important;
        font-weight: 400 !important;
    }}

    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {{
        height: 32px !important;
        width: 32px !important;
    }}

    label[data-testid="stWidgetLabel"] p {{
        font-size: 20px !important;
        font-weight: 700 !important;
    }}

    .section-title {{
        font-size: 20px;
        font-weight: 800;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }}

    .matrix-scroll {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }}

    .matrix-table {{
        width: 100%;
        min-width: 620px;
        table-layout: auto;
        border-collapse: collapse;
    }}

    .matrix-table thead th {{
        font-size: 14px;
        font-weight: 800;
        padding: 0px 04px 08px 00px;
        text-align: center;
        border-bottom: 1px solid {COLORS["border"]};
        white-space: nowrap;
        background: {COLORS["header_bg"]};
        color: {COLORS["text"]};
    }}

    .matrix-table thead th:first-child,
    .matrix-table tbody td:first-child {{
        position: sticky;
        left: 0;
        z-index: 3;
        background: {COLORS["sticky_bg"]};
        text-align: left !important;
        color: {COLORS["text"]};
        width: 70px;
        min-width: 70px;
        max-width: 70px;
    }}

    .matrix-table thead th:first-child {{
        width: 70px;
        min-width: 70px;
        max-width: 70px;
        z-index: 4;
    }}

    .matrix-kpi-cell {{
        font-size: 14px;
        font-weight: 700;
        padding-top: 10px;
        line-height: 1.05;
        width: 115px;
        min-width: 115px;
        max-width: 115px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        color: {COLORS["text"]};
    }}

    .matrix-value-card {{
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 1px 1px 1px 1px;
        min-height: 12px;
        background: {COLORS["card_bg"]};
        display: flex;
        align-items: center;
    }}

    .matrix-value {{
        font-size: 15px;
        font-weight: 600;
        line-height: 1.05;
        word-break: break-word;
        color: {COLORS["text"]};
        padding: 0 2px;
        text-align: center;
    }}

    .matrix-value.positive {{
        color: {COLORS["positive"]};
    }}

    .matrix-value.negative {{
        color: {COLORS["negative"]};
    }}

    .matrix-value.neutral {{
        color: {COLORS["text"]};
    }}

    @media (max-width: 768px) {{
        .matrix-table {{
            min-width: 620px;
        }}

        .matrix-value {{
            font-size: 15px;
        }}

        .matrix-kpi-cell {{
            font-size: 13px;
            min-width: 70px;
            max-width: 70px;
        }}

        .section-title {{
            font-size: 18px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================
# PATH
# =====================================

BASE_DIR = pathlib.Path(__file__).resolve().parent

# =====================================
# LOAD ACTUAL DATA
# =====================================

@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / "data" / "kpi_table.csv")

    df.columns = (
        df.columns
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.strip()
    )

    return df

# =====================================
# LOAD METRIC FILES
# =====================================

@st.cache_data
def load_metric_file(filename):
    df = pd.read_csv(
        BASE_DIR / "data" / filename,
        header=None,
        names=["SalesRoom", "Metric", "Value"],
        encoding="latin1"
    )

    df["SalesRoom"] = df["SalesRoom"].astype(str).str.strip()
    df["Metric"] = df["Metric"].astype(str).str.strip()
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    def clean_metric(x):
        x = str(x).strip()

        if "Penetr" in x:
            return "Penetration"

        x = x.replace("Q’s", "Qs").replace("Q´s", "Qs").replace("Q's", "Qs")
        x = x.replace("Contracts ", "Contracts").replace("Average Price ", "Average Price")
        x = x.replace("Closing Rate ", "Closing Rate").replace("VPG ", "VPG")
        x = x.replace("Volume ", "Volume").replace("Arrivals ", "Arrivals")

        return x

    df["Metric"] = df["Metric"].apply(clean_metric)

    df = df.pivot_table(
        index="SalesRoom",
        columns="Metric",
        values="Value",
        aggfunc="first"
    ).reset_index()

    df.columns.name = None
    return df

# =====================================
# LOAD DATAFRAMES
# =====================================

df = load_data()
forecast_df = load_metric_file("May_Forecast.csv")
budget_df = load_metric_file("Jun_Budget.csv")

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

def numeric_col(frame, col):
    if col not in frame.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(frame[col], errors="coerce").fillna(0)

def aggregate_actual_defaults(actual_subset):
    arrivals = float(numeric_col(actual_subset, "Arrivals").sum())
    contracts_series = numeric_col(actual_subset, "Contracts Processable")
    closing_series = pd.to_numeric(actual_subset["Closing Rate"], errors="coerce").fillna(0) if "Closing Rate" in actual_subset.columns else pd.Series(dtype=float)
    avg_price_series = pd.to_numeric(actual_subset["Average Price"], errors="coerce").fillna(0) if "Average Price" in actual_subset.columns else pd.Series(dtype=float)

    contracts = float(contracts_series.sum())

    total_qs = 0.0
    total_volume = 0.0

    for c, cr, ap in zip(
        contracts_series.tolist(),
        closing_series.tolist() if len(closing_series) else [0] * len(contracts_series),
        avg_price_series.tolist() if len(avg_price_series) else [0] * len(contracts_series),
    ):
        cr_pct = normalize_percent(cr)
        if cr_pct > 0 and pd.notna(c):
            total_qs += float(c) / (cr_pct / 100)

        if pd.notna(c) and pd.notna(ap):
            total_volume += float(c) * float(ap)

    closing_rate = (contracts / total_qs * 100) if total_qs else 0
    avg_price = (total_volume / contracts) if contracts else 0

    return arrivals, contracts, closing_rate, avg_price

def aggregate_metric_defaults(metric_df, salesrooms):
    subset = metric_df[metric_df["SalesRoom"].isin(salesrooms)].copy()

    arrivals = float(numeric_col(subset, "Arrivals").sum())
    contracts = float(numeric_col(subset, "Contracts").sum())
    qs = float(numeric_col(subset, "Qs").sum())
    volume = float(numeric_col(subset, "Volume").sum())

    penetration = (qs / arrivals * 100) if arrivals else 0
    closing_rate = (contracts / qs * 100) if qs else 0
    avg_price = (volume / contracts) if contracts else 0
    vpg = (volume / qs) if qs else 0

    return {
        "Arrivals": arrivals,
        "Contracts": contracts,
        "Qs": qs,
        "Volume": volume,
        "Penetration": penetration,
        "Closing Rate": closing_rate,
        "Average Price": avg_price,
        "VPG": vpg,
    }

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

def fmt_matrix(kind, value, variance=False):
    if kind == "int":
        return f"{value:+,.0f}" if variance else f"{value:,.0f}"
    if kind == "money":
        return f"${value:+,.0f}" if variance else f"${value:,.0f}"
    if kind == "pct":
        return f"{value:+.2f} pp" if variance else f"{value:.2f}%"
    return str(value)

def value_card(value, tone="neutral"):
    return f"""
    <div class="matrix-value {tone}">{html.escape(value)}</div>
    """

def render_matrix(rows):

    html_out = f"""
    <html>
    <head>
      <style>
        body {{
          margin: 0;
          padding: 0;
          background: {COLORS["bg"]};
          color: {COLORS["text"]};
          font-family: sans-serif;
        }}

        .matrix-shell {{
            background: {COLORS["bg"]};
            border-radius: 14px;
            padding: 2px 0 0 0;
        }}

        .matrix-scroll {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .matrix-table {{
            width: 100%;
            min-width: 820px;
            table-layout: auto;
            border-collapse: collapse;
        }}

        .matrix-table col.kpi-col {{
            width: 90px;
        }}

        .matrix-table col.actual-col {{
            width: 90px;
        }}

        .matrix-table col.projected-col {{
            width: 95px;
        }}

        .matrix-table col.forecast-col {{
            width: 95px;
        }}

        .matrix-table col.variance-col {{
            width: 95px;
        }}

        .matrix-table col.budget-col {{
            width: 95px;
        }}

        .matrix-table thead th {{
            font-size: 13px;
            font-weight: 700;
            padding-top: 0px;
            padding-bottom: 4px;
            padding-left: 0px;
            padding-right: 0px;
            text-align: center;
            border-bottom: 1px solid {COLORS["border"]};
            white-space: nowrap;
            background: {COLORS["header_bg"]};
            color: {COLORS["text"]};
        }}

        .matrix-table tbody td {{
            padding-top: 1px;
            padding-bottom: 1px;
            padding-left: 0px;
            padding-right: 0px;
            text-align: center;
        }}

        .matrix-table thead th:first-child,
        .matrix-table tbody td:first-child {{
            position: sticky;
            left: 0;
            z-index: 3;
            background: {COLORS["sticky_bg"]};
            text-align: left !important;
            color: {COLORS["text"]};
            width: auto;
            min-width: 115px;
            max-width: 115px;
        }}

        .matrix-table thead th:first-child {{
            z-index: 4;
        }}

        .matrix-kpi-cell {{
            font-size: 13px;
            font-weight: 700;
            padding-top: 4px;
            line-height: 1.05;
            width: auto;
            min-width: 150px;
            max-width: none;
            overflow: visible;
            white-space: nowrap;
            text-overflow: clip;
            color: {COLORS["text"]};
        }}

        .matrix-value-card {{
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 0px;
            padding-right: 0px;
            min-height: auto;
            background: transparent;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .matrix-value {{
            font-size: 14px;
            font-weight: 700;
            line-height: 1.05;
            word-break: break-word;
            color: {COLORS["text"]};
            text-align: center;
        }}

        .matrix-value.positive {{
            color: {COLORS["positive"]};
        }}

        .matrix-value.negative {{
            color: {COLORS["negative"]};
        }}

        .matrix-value.neutral {{
            color: {COLORS["text"]};
        }}

        @media (max-width: 768px) {{
            .matrix-table {{
                min-width: 820px;
            }}

            .matrix-table thead th {{
                font-size: 11px;
            }}

            .matrix-kpi-cell {{
                font-size: 12px;
                min-width: 120px;
            }}

            .matrix-value {{
                font-size: 12px;
            }}
        }}
      </style>
    </head>

    <body>
      <div class="matrix-shell">
        <div class="matrix-scroll">
          <table class="matrix-table">
            <colgroup>
              <col class="kpi-col">
              <col class="actual-col">
              <col class="projected-col">
              <col class="forecast-col">
              <col class="variance-col">
              <col class="budget-col">
              <col class="variance-col">
            </colgroup>

            <thead>
              <tr>
                <th style="text-align:left;">KPI</th>
                <th>Actuals</th>
                <th>Projected</th>
                <th>Forecast</th>
                <th>Var vs Fcst</th>
                <th>Budget</th>
                <th>Var vs Budget</th>
              </tr>
            </thead>

            <tbody>
    """

    for label, actual, projected, forecast, budget, var_vs_fcst, var_vs_budget, kind in rows:

        tone_fcst = "neutral"
        tone_budget = "neutral"

        if var_vs_fcst > 0:
            tone_fcst = "positive"
        elif var_vs_fcst < 0:
            tone_fcst = "negative"

        if var_vs_budget > 0:
            tone_budget = "positive"
        elif var_vs_budget < 0:
            tone_budget = "negative"

        html_out += f"""
              <tr>
                <td>
                  <div class="matrix-kpi-cell">
                    {html.escape(label)}
                  </div>
                </td>

                <td>{value_card(fmt_matrix(kind, actual), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, projected), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, forecast), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, var_vs_fcst, variance=True), tone=tone_fcst)}</td>
                <td>{value_card(fmt_matrix(kind, budget), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, var_vs_budget, variance=True), tone=tone_budget)}</td>
              </tr>
        """

    html_out += """
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    """

    height = 100 + (len(rows) * 34)

    st.components.v1.html(
        html_out,
        height=height,
        scrolling=True
    )

# =====================================
# PROJECT LEADER / SALESROOM FILTER
# =====================================

all_salesrooms = sorted(df["SalesRoom"].dropna().astype(str).unique().tolist())

project_leader = st.selectbox(
    "Select Project Leader",
    list(PROJECT_LEADERS.keys())
)

if project_leader == "ALL":
    leader_salesrooms = all_salesrooms
else:
    leader_salesrooms = PROJECT_LEADERS[project_leader]

salesroom_options = ["ALL"] + leader_salesrooms

salesroom = st.selectbox(
    "Select SalesRoom",
    salesroom_options
)

if salesroom == "ALL":
    selected_salesrooms = leader_salesrooms
else:
    selected_salesrooms = [salesroom]

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
    leader_salesrooms = sorted(
        df["SalesRoom"].dropna().astype(str).unique().tolist(),
        key=str.lower
    )
else:
    leader_salesrooms = sorted(
        PROJECT_LEADERS[project_leader],
        key=str.lower
    )

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
    arrivals = input_card(
        "Arrivals",
        int(round(float(actual_arrivals))),
        step=1,
        fmt="%d"
    )

with i2:
    contracts = input_card(
        "Contracts",
        int(round(float(actual_contracts))),
        step=1,
        fmt="%d"
    )

with i3:
    closing_rate = input_card(
        "Closing Rate %",
        float(actual_closing_rate),
        step=0.1,
        fmt="%.1f"
    )

with i4:
    avg_price = input_card(
        "Average Price ($)",
        int(round(float(actual_avg_price))),
        step=100,
        fmt="%d"
    )

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

render_matrix(matrix_rows)
