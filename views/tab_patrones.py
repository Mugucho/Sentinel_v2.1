import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from collections import defaultdict


def find_ihs_patterns(df):
    """
    Lógica extraída de TechnicalChartPatternsAlpaca.ipynb
    Detecta patrones IHS (Hombro-Cabeza-Hombro Invertido)
    """
    patterns = defaultdict(list)
    prices = df["Close"].values

    # El patrón IHS requiere al menos 5 puntos clave (A, B, C, D, E)
    for i in range(5, len(prices)):
        window = prices[i - 5 : i]
        a, b, c, d, e = window

        # Lógica IHS: Cabeza (c) más baja que hombros (a, e)
        # Y hombros (b, d) a niveles similares (cuello)
        if (
            a < b
            and c < a
            and c < e
            and c < d
            and e < d
            and abs(b - d) <= np.mean([b, d]) * 0.02
        ):
            patterns["IHS"].append(i)

    return patterns


def render_patrones_tab(ticker):
    st.subheader(f"🔍 Reconocimiento de Patrones: {ticker}")
    st.markdown(
        "Detección algorítmica de formaciones chartistas clásicas (IHS, Doble Suelo, etc.)"
    )

    with st.spinner("Analizando estructuras de precio..."):
        df = yf.download(ticker, period="1mo", interval="1h", progress=False)
        if df.empty:
            st.error("No se pudieron obtener datos para el análisis de patrones.")
            return

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 1. Asegurar zona horaria limpia (vital para evitar desfases en Plotly)
        if df.index.tz is not None:
            df.index = df.index.tz_convert("America/New_York").tz_localize(None)

        # 2. Filtrar para incluir solo las horas de mercado regular (9:30 a 16:00 ET)
        df = df.between_time("09:30", "16:00")

        patterns = find_ihs_patterns(df)

        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Precio",
            )
        )

        # Marcar patrones detectados
        for idx in patterns["IHS"]:
            fig.add_annotation(
                x=df.index[idx],
                y=df["Low"].iloc[idx],
                text="IHS",
                showarrow=True,
                arrowhead=1,
                bgcolor="green",
                font=dict(color="white"),
            )

        # === CORRECCIÓN VISUAL: ELIMINAR HUECOS INTRADIARIOS ===
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),  # Oculta fines de semana
                dict(bounds=[16, 9.5], pattern="hour"),  # Oculta horas nocturnas
            ]
        )

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=40, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)

        if not patterns["IHS"]:
            st.info("No se detectaron patrones IHS claros en el periodo de 1 mes (H1).")
