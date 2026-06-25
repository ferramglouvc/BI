import html
import streamlit as st
from utils.formatting import fmt_matrix


def value_card(value, tone="neutral"):
    return f"""
    <div class="matrix-value {tone}">{html.escape(value)}</div>
    """


def render_matrix(rows, colors):
    html_out = f"""
    <html>
    <head>
      <style>
        body {{
          margin: 0;
          padding: 0;
          background: {colors["bg"]};
          color: {colors["text"]};
          font-family: sans-serif;
        }}

        .matrix-shell {{
            background: {colors["bg"]};
            border-radius: 14px;
            padding: 0;
            margin: 0;
        }}

        .matrix-scroll {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 0;
            padding: 0;
        }}

        .matrix-table {{
            width: 100%;
            min-width: 720px;
            table-layout: fixed;
            border-collapse: collapse;
            margin: 0;
        }}

        .matrix-table col.kpi-col {{
            width: 80px;
        }}

        .matrix-table col.actual-col {{
            width: 90px;
        }}

        .matrix-table col.projected-col {{
            width: 95px;
        }}

        .matrix-table col.forecast-col {{
            width: 95px;
        }}

        .matrix-table col.variance-col {{
            width: 95px;
        }}

        .matrix-table col.budget-col {{
            width: 95px;
        }}

        .matrix-table thead th {{
            font-size: 13px;
            font-weight: 700;
            padding: 0px 4px 3px 0px;
            text-align: center;
            border-bottom: 1px solid {colors["border"]};
            white-space: nowrap;
            background: {colors["header_bg"]};
            color: {colors["text"]};
        }}

        .matrix-table tbody td {{
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 0px;
            padding-right: 0px;
            text-align: center;
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
            padding-top: 2px;
            line-height: 1.0;
            width: 80px;
            min-width: 80px;
            max-width: 80px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            color: {colors["text"]};
        }}

        .matrix-value-card {{
            padding: 0;
            min-height: auto;
            background: transparent;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .matrix-value {{
            font-size: 13px;
            font-weight: 700;
            line-height: 1.0;
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
      </style>
    </head>

    <body>
      <div class="matrix-shell">
        <div class="matrix-scroll">
          <table class="matrix-table">
            <colgroup>
              <col class="kpi-col">
              <col class="actual-col">
              <col class="projected-col">
              <col class="forecast-col">
              <col class="variance-col">
              <col class="budget-col">
              <col class="variance-col">
            </colgroup>

            <thead>
              <tr>
                <th style="text-align:left;">KPI</th>
                <th>Actuals</th>
                <th>Projected</th>
                <th>Forecast</th>
                <th>Var vs Fcst</th>
                <th>Budget</th>
                <th>Var vs Budget</th>
              </tr>
            </thead>

            <tbody>
    """

    for label, actual, projected, forecast, budget, var_vs_fcst, var_vs_budget, kind in rows:
        tone_fcst = "neutral"
        tone_budget = "neutral"

        if var_vs_fcst > 0:
            tone_fcst = "positive"
        elif var_vs_fcst < 0:
            tone_fcst = "negative"

        if var_vs_budget > 0:
            tone_budget = "positive"
        elif var_vs_budget < 0:
            tone_budget = "negative"

        html_out += f"""
              <tr>
                <td>
                  <div class="matrix-kpi-cell">{html.escape(label)}</div>
                </td>

                <td>{value_card(fmt_matrix(kind, actual), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, projected), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, forecast), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, var_vs_fcst, variance=True), tone=tone_fcst)}</td>
                <td>{value_card(fmt_matrix(kind, budget), tone="neutral")}</td>
                <td>{value_card(fmt_matrix(kind, var_vs_budget, variance=True), tone=tone_budget)}</td>
              </tr>
        """

    html_out += """
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    """

    height = 270

    st.components.v1.html(
        html_out,
        height=height,
        scrolling=True
    )
