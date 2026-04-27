import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from src.data_fetcher import fetch_stock_data


def render_tecnico_tab(ticker):
    st.subheader(f"🧲 Análisis Técnico & VSA: {ticker}")
    with st.spinner("Descargando micro-estructura del mercado..."):
        # Usamos el motor centralizado para consistencia
        df = fetch_stock_data(ticker, period_days=5, interval="5m")
        if df.empty:
            st.error("Error al descargar datos.")
            return

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 1. Renombrar el índice a 'Date' si es necesario y asegurar zona horaria limpia
        df = df.reset_index().rename(columns={"index": "Date"})
        df["Date"] = (
            pd.to_datetime(df["Date"])
            .dt.tz_convert("America/New_York")
            .tz_localize(None)
        )

        # 2. Filtrar para incluir solo las horas de mercado regular (9:30 a 16:00 ET)
        df = df.between_time("09:30", "16:00")

        # 3. Calcular VWAP
        df.ta.vwap(append=True)
        vwap_col = [c for c in df.columns if "VWAP" in c][0]

        # 4. Generar Gráfico
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Precio",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[vwap_col],
                mode="lines",
                name="VWAP (Institucional)",
                line=dict(color="#FFD700", width=2, dash="dot"),
            )
        )

        # === LA MAGIA VISUAL: ELIMINAR HUECOS INTRADIARIOS ===
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),  # Oculta fines de semana
                dict(bounds=[16, 9.5], pattern="hour"),  # Oculta horas nocturnas
            ]
        )

        fig.update_layout(
            template="plotly_dark",
            title="Acción del Precio vs VWAP Intradiario",
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=10, r=10, t=40, b=10),
        )

        # use_container_width es la forma actualizada de Streamlit para ancho completo
        st.plotly_chart(fig, use_container_width=True)
