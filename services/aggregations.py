import pandas as pd


# =====================================
# INTERNAL HELPERS
# =====================================

def _numeric_series(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:
    """Return a numeric Series, or zeros when the column is absent."""

    if column not in df.columns:
        return pd.Series(
            0.0,
            index=df.index,
            dtype="float64",
        )

    return pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(0.0)


def _normalize_metric_name(value: object) -> str:
    """Normalize metric names used by long-format target files."""

    text = str(value).strip()

    if "Penetr" in text:
        return "Penetration"

    replacements = {
        "Q's": "Qs",
        "Q’s": "Qs",
        "Q´s": "Qs",
        "Contracts Processable": "Contracts",
        "Reservations Arrivals": "Arrivals",
        "Average Price": "Average Price",
        "Closing Rate": "Closing Rate",
        "Arrivals": "Arrivals",
        "Contracts": "Contracts",
        "VPG": "VPG",
        "Volume": "Volume",
    }

    return replacements.get(text, text)


def _empty_metric_summary() -> dict[str, float]:
    return {
        "Arrivals": 0.0,
        "Penetration": 0.0,
        "Qs": 0.0,
        "Contracts": 0.0,
        "Average Price": 0.0,
        "Closing Rate": 0.0,
        "VPG": 0.0,
        "Volume": 0.0,
    }


# =====================================
# ACTUALS AGGREGATION
# =====================================

def aggregate_actual_defaults(
    df: pd.DataFrame,
) -> tuple[float, float, float, float]:
    """
    Aggregate actual values for the selected context.

    Arrivals is repeated across Membership Type rows, so it is counted
    once per SalesRoom and Sales Type. Average Price is contract-weighted.
    Closing Rate is rebuilt from total Contracts and estimated total Qs.

    Returns:
        arrivals, contracts, closing_rate_percentage, average_price
    """

    if df.empty:
        return 0.0, 0.0, 0.0, 0.0

    work = df.copy()

    work["Arrivals"] = _numeric_series(work, "Arrivals")
    work["Contracts Processable"] = _numeric_series(
        work,
        "Contracts Processable",
    )
    work["Average Price"] = _numeric_series(work, "Average Price")
    work["Closing Rate"] = _numeric_series(work, "Closing Rate")

    arrival_group_columns = [
        column
        for column in ("SalesRoom", "Sales Type")
        if column in work.columns
    ]

    if arrival_group_columns:
        arrivals = float(
            work.drop_duplicates(
                subset=arrival_group_columns,
            )["Arrivals"].sum()
        )
    else:
        arrivals = float(work["Arrivals"].max())

    contracts = float(
        work["Contracts Processable"].sum()
    )

    volume = float(
        (
            work["Average Price"]
            * work["Contracts Processable"]
        ).sum()
    )

    avg_price = (
        volume / contracts
        if contracts > 0
        else 0.0
    )

    valid_rates = work[
        (work["Closing Rate"] > 0)
        & (work["Contracts Processable"] > 0)
    ].copy()

    if valid_rates.empty:
        closing_rate_pct = 0.0
    else:
        total_qs = float(
            (
                valid_rates["Contracts Processable"]
                / valid_rates["Closing Rate"]
            ).sum()
        )

        closing_rate_pct = (
            contracts / total_qs * 100
            if total_qs > 0
            else 0.0
        )

    return (
        arrivals,
        contracts,
        float(closing_rate_pct),
        float(avg_price),
    )


# =====================================
# FORECAST / BUDGET AGGREGATION
# =====================================

def summarize_metric_subset(
    df: pd.DataFrame,
) -> dict[str, float]:
    """
    Summarize Forecast or Budget for one or more SalesRooms.

    Supports long format (SalesRoom, Metric, Value) and wide format.
    Additive metrics are summed and ratios are rebuilt from totals when
    the required additive inputs are available.
    """

    if df.empty:
        return _empty_metric_summary()

    work = df.copy()

    if {"Metric", "Value"}.issubset(work.columns):
        work["Metric"] = work["Metric"].map(_normalize_metric_name)
        work["Value"] = pd.to_numeric(
            work["Value"],
            errors="coerce",
        ).fillna(0.0)

        grouped = work.groupby(
            "Metric",
            dropna=False,
        )["Value"].sum()

        arrivals = float(grouped.get("Arrivals", 0.0))
        qs = float(grouped.get("Qs", 0.0))
        contracts = float(grouped.get("Contracts", 0.0))
        volume = float(grouped.get("Volume", 0.0))

        def metric_mean(metric_name: str) -> float:
            mask = work["Metric"].eq(metric_name)
            if not mask.any():
                return 0.0
            return float(work.loc[mask, "Value"].mean())

        raw_avg_price = metric_mean("Average Price")
        raw_closing_rate = metric_mean("Closing Rate")
        raw_penetration = metric_mean("Penetration")
        raw_vpg = metric_mean("VPG")

    else:
        if (
            "Contracts" not in work.columns
            and "Contracts Processable" in work.columns
        ):
            work = work.rename(
                columns={
                    "Contracts Processable": "Contracts",
                }
            )

        arrivals_series = _numeric_series(work, "Arrivals")
        qs_series = _numeric_series(work, "Qs")
        contracts_series = _numeric_series(work, "Contracts")
        avg_price_series = _numeric_series(work, "Average Price")
        closing_rate_series = _numeric_series(work, "Closing Rate")
        penetration_series = _numeric_series(work, "Penetration")
        vpg_series = _numeric_series(work, "VPG")
        volume_series = _numeric_series(work, "Volume")

        arrivals = float(arrivals_series.sum())
        qs = float(qs_series.sum())
        contracts = float(contracts_series.sum())
        volume = float(volume_series.sum())

        if volume == 0 and contracts > 0:
            volume = float(
                (avg_price_series * contracts_series).sum()
            )

        raw_avg_price = float(avg_price_series.mean())
        raw_closing_rate = float(closing_rate_series.mean())
        raw_penetration = float(penetration_series.mean())
        raw_vpg = float(vpg_series.mean())

    avg_price = (
        volume / contracts
        if contracts > 0 and volume > 0
        else raw_avg_price
    )

    closing_rate = (
        contracts / qs * 100
        if qs > 0
        else (
            raw_closing_rate * 100
            if 0 < raw_closing_rate <= 1
            else raw_closing_rate
        )
    )

    penetration = (
        qs / arrivals * 100
        if arrivals > 0 and qs > 0
        else (
            raw_penetration * 100
            if 0 < raw_penetration <= 1
            else raw_penetration
        )
    )

    vpg = (
        volume / qs
        if qs > 0 and volume > 0
        else raw_vpg
    )

    return {
        "Arrivals": float(arrivals),
        "Penetration": float(penetration),
        "Qs": float(qs),
        "Contracts": float(contracts),
        "Average Price": float(avg_price),
        "Closing Rate": float(closing_rate),
        "VPG": float(vpg),
        "Volume": float(volume),
    }
