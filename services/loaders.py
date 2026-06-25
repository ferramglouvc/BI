import pathlib
import pandas as pd
import streamlit as st

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


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
