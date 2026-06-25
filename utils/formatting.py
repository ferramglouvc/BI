def fmt_matrix(kind, value, variance=False):
    if kind == "int":
        return f"{value:+,.0f}" if variance else f"{value:,.0f}"
    if kind == "money":
        return f"${value:+,.0f}" if variance else f"${value:,.0f}"
    if kind == "pct":
        return f"{value:+.2f} pp" if variance else f"{value:.2f}%"
    return str(value)
