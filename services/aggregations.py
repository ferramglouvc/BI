import pandas as pd


# =====================================
# INTERNAL HELPERS
# =====================================

def _numeric_series(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:
    """
    Return a numeric Series for a column.

    Missing columns return a Series of zeros with
    the same index as the DataFrame.
    """

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
    """
    Normalize names used by long-format target files.
    """

    text = str(value).strip()

    if "Penetr" in text:
        return "Penetration"

    replacements = {
        "Q's": "Qs",
        "Q’s": "Qs",
        "Q´s": "Qs",
        "Contracts Processable": "Contracts",
        "Average Price": "Average Price",
        "Closing Rate": "Closing Rate",
        "Reservations Arrivals": "Arrivals",
        "Arrivals": "Arrivals",
        "Contracts": "Contracts",
        "VPG": "VPG",
        "Volume": "Volume",
    }

    return replacements.get(text, text)


def _empty_metric_summary() -> dict[str, float]:
    """
    Return the metric structure expected by streamlit_app.py.
    """

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

    Important:
    Arrivals is repeated across Membership Type rows.
    It is counted once per SalesRoom and Sales Type.

    Returns:
        arrivals
        contracts
        closing_rate_percentage
        average_price
    """

    if df.empty:
        return 0.0, 0.0, 0.0, 0.0

    work = df.copy()

    work["Arrivals"] = _numeric_series(
        work,
        "Arrivals",
    )

    work["Contracts Processable"] = _numeric_series(
        work,
        "Contracts Processable",
    )

    work["Average Price"] = _numeric_series(
        work,
        "Average Price",
    )

    work["Closing Rate"] = _numeric_series(
        work,
        "Closing Rate",
    )

    # ---------------------------------
    # ARRIVALS
    # ---------------------------------
    # Arrivals repeats for every membership row.
    # Count it once per SalesRoom + Sales Type.
    arrival_group_columns = [
        column
        for column in [
            "SalesRoom",
            "Sales Type",
        ]
        if column in work.columns
    ]

    if arrival_group_columns:
        arrival_rows = work.drop_duplicates(
            subset=arrival_group_columns
        )

        arrivals = float(
            arrival_rows["Arrivals"].sum()
        )
    else:
        # Fallback when grouping columns are unavailable.
        arrivals = float(
            work["Arrivals"].max()
        )

    # ---------------------------------
    # CONTRACTS
    # ---------------------------------

    contracts = float(
        work["Contracts Processable"].sum()
    )

    # ---------------------------------
    # VOLUME / AVERAGE PRICE
    # ---------------------------------

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

    # ---------------------------------
    # CLOSING RATE
    # ---------------------------------
    # In kpi_table.csv Closing Rate is a ratio:
    # 0.40 = 40%
    # 1.50 = 150%
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
        float(arrivals),
        float(contracts),
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

    Supports:
    1. Wide format:
       SalesRoom, Arrivals, Qs, Contracts, Volume, etc.

    2. Long format:
       SalesRoom, Metric, Value

    Additive metrics are summed. Ratios are recalculated
    from the additive totals instead of being averaged.
    """

    if df.empty:
        return _empty_metric_summary()

    work = df.copy()

    # ---------------------------------
    # LONG FORMAT
    # ---------------------------------

    if {"Metric", "Value"}.issubset(work.columns):
        work["Metric"] = (
            work["Metric"]
            .map(_normalize_metric_name)
        )

        work["Value"] = pd.to_numeric(
            work["Value"],
            errors="coerce",
        ).fillna(0.0)

        grouped = (
            work.groupby(
                "Metric",
                dropna=False,
            )["Value"]
            .sum()
        )

        arrivals = float(
            grouped.get("Arrivals", 0.0)
        )

        qs = float(
            grouped.get("Qs", 0.0)
        )

        contracts = float(
            grouped.get("Contracts", 0.0)
        )

        volume = float(
            grouped.get("Volume", 0.0)
        )

        # Fallback values only if additive metrics
        # are not present in the file.
        raw_avg_price = float(
            work.loc[
                work["Metric"].eq("Average Price"),
                "Value",
            ].mean()
        ) if work["Metric"].eq("Average Price").any() else 0.0

        raw_closing_rate = float(
            work.loc[
                work["Metric"].eq("Closing Rate"),
                "Value",
            ].mean()
        ) if work["Metric"].eq("Closing Rate").any() else 0.0

        raw_penetration = float(
            work.loc[
                work["Metric"].eq("Penetration"),
                "Value",
            ].mean()
        ) if work["Metric"].eq("Penetration").any() else 0.0

        raw_vpg = float(
            work.loc[
                work["Metric"].eq("VPG"),
                "Value",
            ].mean()
        ) if work["Metric"].eq("VPG").any() else 0.0

    # ---------------------------------
    # WIDE FORMAT
    # ---------------------------------

    else:
        # Accept Contracts or Contracts Processable.
        if (
            "Contracts" not in work.columns
            and "Contracts Processable" in work.columns
        ):
            work = work.rename(
                columns={
                    "Contracts Processable": "Contracts"
                }
            )

        arrivals_series = _numeric_series(
            work,
            "Arrivals",
        )

        qs_series = _numeric_series(
            work,
            "Qs",
        )

        contracts_series = _numeric_series(
            work,
            "Contracts",
        )

        avg_price_series = _numeric_series(
            work,
            "Average Price",
        )

        closing_rate_series = _numeric_series(
            work,
            "Closing Rate",
        )

        penetration_series = _numeric_series(
            work,
            "Penetration",
        )

        vpg_series = _numeric_series(
            work,
            "VPG",
        )

        volume_series = _numeric_series(
            work,
            "Volume",
        )

        arrivals = float(
            arrivals_series.sum()
        )

        qs = float(
            qs_series.sum()
        )

        contracts = float(
            contracts_series.sum()
        )

        volume = float(
            volume_series.sum()
        )

        # Derive Volume when target files do not
        # provide it explicitly.
        if volume == 0 and contracts > 0:
            volume = float(
                (
                    avg_price_series
                    * contracts_series
                ).sum()
            )

        raw_avg_price = float(
            avg_price_series.mean()
        ) if not avg_price_series.empty else 0.0

        raw_closing_rate = float(
            closing_rate_series.mean()
        ) if not closing_rate_series.empty else 0.0

        raw_penetration = float(
            penetration_series.mean()
        ) if not penetration_series.empty else 0.0

        raw_vpg = float(
            vpg_series.mean()
        ) if not vpg_series.empty else 0.0

    # ---------------------------------
    # DERIVED SUMMARY KPIs
    # ---------------------------------

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
        if arrivals > 0
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
