import streamlit as st


def apply_styles(colors):
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: {colors["bg"]};
            color: {colors["text"]};
        }}

        [data-testid="stHeader"] {{
            background: {colors["bg"]};
        }}

        [data-testid="stSidebar"] {{
            background: {colors["bg"]};
        }}

        .stApp {{
            background: {colors["bg"]};
            color: {colors["text"]};
        }}

        .block-container {{
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 1rem;
        }}

        div[data-baseweb="input"] input {{
            font-size: 16px !important;
            font-weight: 400 !important;
        }}

        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"] {{
            height: 24px !important;
            width: 24px !important;
        }}

        label[data-testid="stWidgetLabel"] p {{
            font-size: 16px !important;
            font-weight: 700 !important;
        }}

        .section-title {{
         font-size: 20px;
    font-weight: 800;
    margin-top: 0rem;
    margin-bottom: 0rem;
}}

.simulator-wrap {{
    padding-top: 0rem;
}}

        .matrix-scroll {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .matrix-table {{
            width: 100%;
            min-width: 720px;
            table-layout: fixed;
            border-collapse: collapse;
        }}

        .matrix-table thead th {{
            font-size: 13px;
            font-weight: 700;
            padding: 0px 4px 4px 0px;
            text-align: center;
            border-bottom: 1px solid {colors["border"]};
            white-space: nowrap;
            background: {colors["header_bg"]};
            color: {colors["text"]};
        }}

        .matrix-table thead th:first-child,
        .matrix-table tbody td:first-child {{
            position: sticky;
            left: 0;
            z-index: 3;
            background: {colors["sticky_bg"]};
            text-align: left !important;
            color: {colors["text"]};
            width: 80px;
            min-width: 80px;
            max-width: 80px;
        }}

        .matrix-table thead th:first-child {{
            z-index: 4;
        }}

        .matrix-kpi-cell {{
            font-size: 13px;
            font-weight: 700;
            padding-top: 4px;
            line-height: 1.05;
            width: 80px;
            min-width: 80px;
            max-width: 80px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            color: {colors["text"]};
        }}

        .matrix-value-card {{
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 1px;
            min-height: 12px;
            background: {colors["card_bg"]};
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .matrix-value {{
            font-size: 14px;
            font-weight: 700;
            line-height: 1.05;
            word-break: break-word;
            color: {colors["text"]};
            text-align: center;
        }}

        .matrix-value.positive {{
            color: {colors["positive"]};
        }}

        .matrix-value.negative {{
            color: {colors["negative"]};
        }}

        .matrix-value.neutral {{
            color: {colors["text"]};
        }}

        div[data-testid="stNumberInputContainer"] {{
            max-width: 150px;
        }}

        div[data-testid="stNumberInput"] input {{
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
            font-size: 14px !important;
        }}

        div[data-testid="stButton"] button {{
            min-height: 2.2rem;
            padding-top: 0.25rem;
            padding-bottom: 0.25rem;
            font-size: 0.9rem;
        }}

        .simulator-wrap {{
            padding-top: 0.0rem;
        }}

        @media (max-width: 768px) {{
            .matrix-table {{
                min-width: 720px;
            }}

            .matrix-table thead th {{
                font-size: 11px;
            }}

            .matrix-kpi-cell {{
                font-size: 11px;
                min-width: 80px;
                max-width: 80px;
            }}

            .matrix-value {{
                font-size: 12px;
            }}
        }}

        @media (max-width: 768px) {{
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 calc(50% - 0.5rem) !important;
        min-width: calc(50% - 0.5rem) !important;
        max-width: calc(50% - 0.5rem) !important;
    }}
}}
        </style>
        """,
        unsafe_allow_html=True,
    )
