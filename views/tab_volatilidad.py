import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def render_volatilidad_tab(ticker):
    st.subheader(f"🪙 Radar Volatilidad: Superficie IV 3D - {ticker}")
    st.markdown(
        "Construcción de la Superficie de Volatilidad Implícita (Calls). Mapeo de *Strike* vs *DTE* vs *IV*."
    )

    if not ticker:
        st.warning("⚠️ Ingresa un ticker válido en el panel lateral de control.")
        return

    with st.spinner(
        f"📡 Descargando cadena de opciones para {ticker}... esto puede tomar unos segundos."
    ):
        try:
            tk = yf.Ticker(ticker)
            expirations = tk.options

            if not expirations:
                st.error(
                    "No hay contratos de opciones disponibles para este activo en el mercado actual."
                )
                return

            # Extraemos datos (Limitamos a las primeras 10 fechas para mantener el Búnker rápido)
            data_frames = []
            today = datetime.today()

            for exp in expirations[:10]:
                opt = tk.option_chain(exp)
                calls = opt.calls

                # Calcular DTE (Days to Expiration)
                exp_date = datetime.strptime(exp, "%Y-%m-%d")
                dte = (exp_date - today).days
                if dte <= 0:
                    dte = 1  # Evitar DTE cero

                calls["DTE"] = dte
                data_frames.append(calls[["strike", "DTE", "impliedVolatility"]])

            # Consolidamos el DataFrame
            df = pd.concat(data_frames)

            # Filtro de ruido: Eliminamos volatilidades ilógicas (ej. 0 o > 300%) que rompen la malla
            df = df[(df["impliedVolatility"] > 0.01) & (df["impliedVolatility"] < 3.0)]

            if df.empty:
                st.warning(
                    "Los datos de volatilidad están sucios o ilíquidos para generar la superficie."
                )
                return

            # Construcción del Gráfico 3D Institucional
            fig = go.Figure(
                data=[
                    go.Mesh3d(
                        x=df["strike"],
                        y=df["DTE"],
                        z=df["impliedVolatility"],
                        intensity=df["impliedVolatility"],
                        colorscale="Plasma",  # Paleta térmica que resalta volatilidades extremas
                        opacity=0.85,
                        name="IV Surface",
                    )
                ]
            )

            # Ajustes de cámara y ejes para el "Plotly Dark"
            fig.update_layout(
                template="plotly_dark",
                height=700,
                margin=dict(l=0, r=0, b=0, t=30),
                scene=dict(
                    xaxis_title="Strike Price ($)",
                    yaxis_title="DTE (Días a Expiración)",
                    zaxis_title="Volatilidad Implícita (IV)",
                    xaxis=dict(gridcolor="gray", backgroundcolor="black"),
                    yaxis=dict(gridcolor="gray", backgroundcolor="black"),
                    zaxis=dict(gridcolor="gray", backgroundcolor="black"),
                    # Ajuste del ángulo de cámara inicial
                    camera=dict(eye=dict(x=1.5, y=1.5, z=0.5)),
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "💡 **Tip de lectura:** Los picos amarillos/claros indican alta prima de riesgo. Busca asimetrías (skew) en los strikes más bajos o más altos para detectar pánico o codicia institucional."
            )

        except Exception as e:
            st.error(f"Error interno al procesar la superficie de volatilidad: {e}")
