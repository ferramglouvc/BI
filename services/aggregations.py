import pandas as pd


def aggregate_actual_defaults(df):
    """
    Aggregate actual values without duplicating Arrivals
    across Membership Type rows.
    """

    work = df.copy()

    numeric_columns = [
        "Average Price",
        "Closing Rate",
        "Arrivals",
        "Contracts Processable",
    ]

    for column in numeric_columns:
        work[column] = pd.to_numeric(
            work[column],
            errors="coerce",
        ).fillna(0.0)

    # Arrivals is repeated across Membership Type rows.
    # Count it only once per SalesRoom and Sales Type.
    arrivals = (
        work[
            [
                "SalesRoom",
                "Sales Type",
                "Arrivals",
            ]
        ]
        .drop_duplicates(
            subset=[
                "SalesRoom",
                "Sales Type",
            ]
        )["Arrivals"]
        .sum()
    )

    contracts = work[
        "Contracts Processable"
    ].sum()

    # Weighted Average Price based on contracts.
    volume = (
        work["Average Price"]
        * work["Contracts Processable"]
    ).sum()

    avg_price = (
        volume / contracts
        if contracts
        else 0.0
    )

    # Closing Rate in this file is stored as a ratio:
    # 0.40 = 40%, 1.50 = 150%, etc.
    valid_closing = work[
        (work["Closing Rate"] > 0)
        & (work["Contracts Processable"] > 0)
    ].copy()

    total_qs = (
        valid_closing["Contracts Processable"]
        / valid_closing["Closing Rate"]
    ).sum()

    closing_rate = (
        contracts / total_qs * 100
        if total_qs
        else 0.0
    )

    return (
        float(arrivals),
        float(contracts),
        float(closing_rate),
        float(avg_price),
    )
