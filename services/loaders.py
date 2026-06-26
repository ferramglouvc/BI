from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_sales_type(value):
    if pd.isna(value):
        return value

    value = str(value).strip()

    mapping = {
        "N": "New Sales",
        "U": "Upgrades",
        "NEW SALES": "New Sales",
        "UPGRADES": "Upgrades",
        "New Sales": "New Sales",
        "Upgrades": "Upgrades",
        "New Sales ": "New Sales",
        " Upgrades": "Upgrades",
    }

    return mapping.get(value, mapping.get(value.upper(), value))


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(BASE_DIR / "data" / "kpi_table.csv")

    df.columns = df.columns.str.strip()

    # Normaliza el nombre de la columna si viene con espacio
    if "Sales Type" in df.columns and "SalesType" not in df.columns:
        df = df.rename(columns={"Sales Type": "SalesType"})

    # Si aún viene con otro nombre parecido, intenta detectarlo
    if "SalesType" not in df.columns:
        for col in df.columns:
            if col.strip().lower() in {"sales type", "salestype"}:
                df = df.rename(columns={col: "SalesType"})
                break

    if "SalesType" in df.columns:
        df["SalesType"] = df["SalesType"].apply(_normalize_sales_type)

    return df


def _clean_metric(x):
    x = str(x).strip()

    if "Penetr" in x:
        return "Penetration"

    x = x.replace("Q’s", "Qs").replace("Q´s", "Qs").replace("Q's", "Qs")
    x = x.replace("Contracts ", "Contracts").replace("Average Price ", "Average Price")
    x = x.replace("Closing Rate ", "Closing Rate").replace("VPG ", "VPG")
    x = x.replace("Volume ", "Volume").replace("Arrivals ", "Arrivals")

    return x


@st.cache_data(show_spinner=False)
def load_metric_file(filename: str, file_mtime: float):
    df = pd.read_csv(
        BASE_DIR / "data" / filename,
        header=None,
        names=["SalesRoom", "Metric", "Value"],
        encoding="latin1",
    )

    df["SalesRoom"] = df["SalesRoom"].astype(str).str.strip()
    df["Metric"] = df["Metric"].astype(str).str.strip().apply(_clean_metric)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df = df.pivot_table(
        index="SalesRoom",
        columns="Metric",
        values="Value",
        aggfunc="first",
    ).reset_index()

    df.columns.name = None
    return df
