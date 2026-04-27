import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render_journal_tab():
    st.subheader("📓 Bitácora de Rendimiento y Psicología")
    st.markdown(
        "Auditoría de ejecución y sesión con formato calendario para detectar overtrading y patrones de desempeño."
    )

    today = datetime.today().date()
    month_options = (
        pd.date_range(end=today, periods=6, freq="ME").to_pydatetime().tolist()
    )
    month_labels = [d.strftime("%B %Y") for d in month_options]
    selected_label = st.selectbox(
        "Seleccionar mes", month_labels, index=len(month_labels) - 1
    )
    selected_date = month_options[month_labels.index(selected_label)].date()

    month_start = selected_date.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    month_end = next_month - timedelta(days=1)

    dates = pd.date_range(start=month_start, end=month_end, freq="D")
    df = pd.DataFrame(
        [
            {
                "Date": d,
                "Trades": 0 if d.weekday() >= 5 else np.random.randint(1, 8),
                "PnL": 0.0 if d.weekday() >= 5 else np.random.uniform(-180, 220),
            }
            for d in dates
        ]
    )
    df["Day"] = df["Date"].dt.day
    df["Weekday"] = df["Date"].dt.weekday
    start_weekday = month_start.weekday()
    df["Week"] = ((df["Day"] + start_weekday - 1) // 7) + 1
    df["Label"] = df.apply(
        lambda row: (
            f"{int(row['Day'])}<br>Weekend"
            if row["Trades"] == 0
            else f"{int(row['Day'])}<br>${row['PnL']:.0f}<br>{int(row['Trades'])} trades"
        ),
        axis=1,
    )

    summary = df.loc[df["Trades"] > 0]
    total_trades = summary["Trades"].sum()
    total_pnl = summary["PnL"].sum()
    positive_days = (summary["PnL"] > 0).sum()
    negative_days = (summary["PnL"] < 0).sum()
    avg_trades = summary["Trades"].mean() if len(summary) > 0 else 0

    st.markdown("### 📌 Resumen Mensual")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Total Trades", f"{int(total_trades)}")
    s2.metric("PnL Total", f"${total_pnl:.0f}")
    s3.metric("Días Positivos", f"{int(positive_days)}")
    s4.metric("Días Negativos", f"{int(negative_days)}")
    s5.metric("Trades/Día", f"{avg_trades:.1f}")

    weeks = df["Week"].max()
    calendar = pd.DataFrame(
        np.full((weeks, 7), None, dtype=object),
        columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    )
    text = pd.DataFrame(
        np.full((weeks, 7), "", dtype=object),
        columns=calendar.columns,
    )
    z = np.full((weeks, 7), np.nan, dtype=float)

    for _, row in df.iterrows():
        w = int(row["Week"] - 1)
        d = int(row["Weekday"])
        calendar.iat[w, d] = row["PnL"]
        text.iat[w, d] = row["Label"]
        z[w, d] = row["PnL"] if row["Trades"] > 0 else np.nan

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=calendar.columns,
            y=[f"Semana {w+1}" for w in range(weeks)],
            text=text.values,
            hoverinfo="text",
            colorscale="RdYlGn",
            zmid=0,
            showscale=False,
            xgap=2,
            ygap=2,
        )
    )
    fig.update_traces(
        texttemplate="%{text}",
        textfont=dict(color="white", size=12),
    )
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(side="top"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=420,
    )

    st.markdown("### 📅 Calendario de Trading Mensual")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### 🧠 Diagnóstico de Fatiga")
    st.write(
        "Este gráfico muestra la relación entre número de trades y PnL para revisar sobretrading."
    )

    fatigue_fig = go.Figure(
        go.Scatter(
            x=df.loc[df["Trades"] > 0, "Trades"],
            y=df.loc[df["Trades"] > 0, "PnL"],
            mode="markers+lines",
            marker=dict(
                color=df.loc[df["Trades"] > 0, "PnL"],
                colorscale="RdYlGn",
                size=df.loc[df["Trades"] > 0, "Trades"] * 3,
                showscale=True,
            ),
        )
    )
    fatigue_fig.add_hline(y=0, line_dash="dash", line_color="white")
    fatigue_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Operaciones",
        yaxis_title="PnL",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fatigue_fig, width="stretch")
