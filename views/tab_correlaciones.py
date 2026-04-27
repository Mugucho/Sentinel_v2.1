import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.broker import AlpacaProvider
from src.data_fetcher import fetch_stock_data
from src.visualizations import create_correlation_heatmap


def render_correlaciones_tab():
    st.subheader("🕸️ Análisis de Correlaciones de Portafolio (Alpaca)")
    st.markdown(
        "Auditoría de riesgo dinámico: Evalúa cómo interactúan las tendencias de tus activos en cartera para identificar riesgos de concentración o descubrir coberturas naturales (hedging)."
    )

    # 1. Conexión con Alpaca para extraer posiciones vivas
    with st.spinner(
        "Conectando con el Búnker de Alpaca para obtener posiciones abiertas..."
    ):
        try:
            alpaca = AlpacaProvider()
            posiciones = alpaca.trading_client.get_all_positions()

            if not posiciones:
                st.warning(
                    "No tienes posiciones abiertas en Alpaca en este momento. Mostrando matriz de riesgo de activos de seguimiento (Watchlist) por defecto."
                )
                # Fallback táctico si la cartera está líquida (vacía)
                tickers = ["SPY", "QQQ", "XLE", "TLT", "GLD"]
            else:
                tickers = [pos.symbol for pos in posiciones]
                st.success(
                    f"📡 Activos activos en cartera detectados: {', '.join(tickers)}"
                )

        except Exception as e:
            st.error(f"Error de enlace con Alpaca: {e}")
            st.info("Usando activos de benchmark por defecto.")
            tickers = ["SPY", "QQQ", "XLE", "TLT", "GLD"]

    if len(tickers) < 2:
        st.warning(
            "El Búnker requiere al menos 2 activos en cartera para calcular una matriz de correlación espacial."
        )
        return

    # 2. Motor de extracción de datos históricos (Últimos 6 meses para correlación)
    with st.spinner("Descargando estructura de precios para análisis vectorial..."):
        data_dict = {}
        for ticker in tickers:
            df = fetch_stock_data(ticker, period_days=180)
            if not df.empty:
                data_dict[ticker] = df

    # 3. Renderizado Cuantitativo
    if len(data_dict) >= 2:
        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown("### 🌡️ Matriz de Correlación (Heatmap)")
            # Utilizamos la función que ya construimos en visualizations.py
            fig_corr = create_correlation_heatmap(data_dict)
            st.plotly_chart(fig_corr, use_container_width=True)

        with col2:
            st.markdown("### 💡 Interpretación de Riesgo")
            st.info(
                """
            **+0.8 a +1.0 (Verde Fuerte): Peligro de Concentración.**
            Ambos activos se mueven idénticos. Si el mercado cae, perderás en ambos. No hay diversificación real.
            """
            )
            st.warning(
                """
            **-0.8 a -1.0 (Rojo Fuerte): Cobertura (Hedging).**
            Se mueven en direcciones opuestas. Si uno cae, el otro sube, protegiendo tu capital (ej. Oro vs Índices en pánico).
            """
            )
            st.success(
                """
            **Cerca de 0.0 (Amarillo/Claro): Diversificación Pura.**
            Los activos son independientes. El movimiento de uno no afecta al otro.
            """
            )

        st.divider()

        # 4. Gráfico de Rendimiento Relativo (Base 0%)
        st.markdown("### 📈 Rendimiento Relativo Acumulado")
        st.caption(
            "Compara la fuerza relativa de tus posiciones normalizando el punto de inicio al 0%."
        )

        fig_rel = go.Figure()

        for ticker, df in data_dict.items():
            # Normalizar a base 0 para comparar rendimientos justamente
            first_price = df["Close"].iloc[0]
            pct_change = ((df["Close"] - first_price) / first_price) * 100

            fig_rel.add_trace(
                go.Scatter(
                    x=df["Date"],
                    y=pct_change,
                    mode="lines",
                    name=ticker,
                    line=dict(width=2),
                )
            )

        # Forzar un eje X continuo sin huecos de fines de semana
        fig_rel.update_xaxes(
            type="category", nticks=15, tickformat="%b %d", showgrid=False
        )

        fig_rel.update_layout(
            template="plotly_dark",
            yaxis_title="Rendimiento Acumulado (%)",
            xaxis_title="Fecha",
            height=450,
            margin=dict(l=10, r=10, t=40, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(fig_rel, use_container_width=True)

    else:
        st.error(
            "No se pudo compilar suficiente data estructurada para comparar los activos de la cartera."
        )
