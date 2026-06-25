import pandas as pd
from utils.formatting import safe_float


def aggregate_actual_defaults(actual_subset):
    arrivals = pd.to_numeric(actual_subset.get("Arrivals"), errors="coerce").fillna(0).sum() if "Arrivals" in actual_subset.columns else 0
    contracts_series = pd.to_numeric(actual_subset.get("Contracts Processable"), errors="coerce").fillna(0) if "Contracts Processable" in actual_subset.columns else pd.Series(dtype=float)
    closing_series = pd.to_numeric(actual_subset.get("Closing Rate"), errors="coerce").fillna(0) if "Closing Rate" in actual_subset.columns else pd.Series(dtype=float)
    avg_price_series = pd.to_numeric(actual_subset.get("Average Price"), errors="coerce").fillna(0) if "Average Price" in actual_subset.columns else pd.Series(dtype=float)

    contracts = float(contracts_series.sum()) if len(contracts_series) else 0
    total_qs = 0.0
    total_volume = 0.0

    for c, cr, ap in zip(
        contracts_series.tolist() if len(contracts_series) else [],
        closing_series.tolist() if len(closing_series) else [],
        avg_price_series.tolist() if len(avg_price_series) else [],
    ):
        cr_pct = safe_float(cr)
        if cr_pct <= 1 and cr_pct > 0:
            cr_pct *= 100

        if c and cr_pct > 0:
            total_qs += float(c) / (cr_pct / 100)

        if c and ap:
            total_volume += float(c) * float(ap)

    closing_rate = (contracts / total_qs * 100) if total_qs else 0
    avg_price = (total_volume / contracts) if contracts else 0

    return float(arrivals), float(contracts), float(closing_rate), float(avg_price)


def summarize_metric_subset(subset: pd.DataFrame):
    totals = {
        "Arrivals": 0.0,
        "Contracts": 0.0,
        "Qs": 0.0,
        "Volume": 0.0,
    }

    for _, row in subset.iterrows():
        arrivals = safe_float(row.get("Arrivals"))
        contracts = safe_float(row.get("Contracts"))
        qs = safe_float(row.get("Qs"))
        closing_rate = safe_float(row.get("Closing Rate"))
        penetration = safe_float(row.get("Penetration"))
        avg_price = safe_float(row.get("Average Price"))
        vpg = safe_float(row.get("VPG"))
        volume = safe_float(row.get("Volume"))

        if closing_rate <= 1 and closing_rate > 0:
            closing_rate *= 100
        if penetration <= 1 and penetration > 0:
            penetration *= 100

        if qs <= 0 and contracts > 0 and closing_rate > 0:
            qs = contracts / (closing_rate / 100)

        if closing_rate <= 0 and contracts > 0 and qs > 0:
            closing_rate = (contracts / qs) * 100

        if arrivals <= 0 and qs > 0 and penetration > 0:
            arrivals = qs / (penetration / 100)

        if penetration <= 0 and qs > 0 and arrivals > 0:
            penetration = (qs / arrivals) * 100

        if volume <= 0 and contracts > 0 and avg_price > 0:
            volume = contracts * avg_price

        if avg_price <= 0 and contracts > 0 and volume > 0:
            avg_price = volume / contracts

        if vpg <= 0 and qs > 0 and volume > 0:
            vpg = volume / qs

        if volume <= 0 and qs > 0 and vpg > 0:
            volume = vpg * qs

        totals["Arrivals"] += arrivals
        totals["Contracts"] += contracts
        totals["Qs"] += qs
        totals["Volume"] += volume

    totals["Closing Rate"] = (totals["Contracts"] / totals["Qs"] * 100) if totals["Qs"] else 0
    totals["Penetration"] = (totals["Qs"] / totals["Arrivals"] * 100) if totals["Arrivals"] else 0
    totals["Average Price"] = (totals["Volume"] / totals["Contracts"]) if totals["Contracts"] else 0
    totals["VPG"] = (totals["Volume"] / totals["Qs"]) if totals["Qs"] else 0

    return totals
