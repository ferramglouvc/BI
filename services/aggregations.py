import pandas as pd


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
    closing_series = (
        pd.to_numeric(actual_subset["Closing Rate"], errors="coerce").fillna(0)
        if "Closing Rate" in actual_subset.columns
        else pd.Series(dtype=float)
    )
    avg_price_series = (
        pd.to_numeric(actual_subset["Average Price"], errors="coerce").fillna(0)
        if "Average Price" in actual_subset.columns
        else pd.Series(dtype=float)
    )

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
