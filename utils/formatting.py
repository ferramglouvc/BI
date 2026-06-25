import pandas as pd


def safe_float(value, default=0.0):
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except Exception:
        return default


def fmt_matrix(kind, value, variance=False):
    if kind == "int":
        return f"{value:+,.0f}" if variance else f"{value:,.0f}"
    if kind == "money":
        return f"${value:+,.0f}" if variance else f"${value:,.0f}"
    if kind == "pct":
        return f"{value:+.2f} pp" if variance else f"{value:.2f}%"
    return str(value)
