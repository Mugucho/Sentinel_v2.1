import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data, fetch_trading_data_alpaca
from src.data_processing import process_data, calculate_support_resistance
from src.pattern_recognition import find_complex_patterns
from src.visualizations import *
from src.mini_platform import (
    run_simulation,
    AlpacaExecutor,
    ALPACA_AVAILABLE,
    TradingEngine,
)
from src.backtest import run_backtest, create_equity_curve_chart
from src.risk_management import drawdown_gate, exposure_gate, reconciliation_gate
from src.oracle import get_market_sentiment


def render_market_lab_tab(ticker):
    st.subheader("📊 Market Lab: Análisis, Simulación y Ejecución")
    st.markdown(
        "Una vista compacta para analizar tendencias, revisar patrones y ejecutar señales con Alpaca (Paper)."
    )

    with st.expander("⚙️ Parámetros de Análisis", expanded=True):
        ticker_input = st.text_input("Ticker para Market Lab", value=ticker).upper()
        ma_window = st.number_input(
            "Ventana SMA", min_value=5, max_value=200, value=50, step=5
        )
        sl_input = st.slider("Stop Loss %", min_value=1, max_value=20, value=5) / 100

    with st.expander("🔑 Credenciales Alpaca", expanded=False):
        api_key = st.text_input("API Key ID", type="password", key="alpaca_api_key")
        secret_key = st.text_input(
            "Secret Key", type="password", key="alpaca_secret_key"
        )
        paper_mode = st.checkbox(
            "Modo Paper Trading", value=True, key="alpaca_paper_mode"
        )

    if not ticker_input:
        st.warning("Ingresa un ticker válido para iniciar el análisis.")
        return

    # --- ARQUITECTURA DE DATOS DUAL ---
    # 1. Datos de yfinance para gráficos y visualizaciones.
    with st.spinner("Descargando datos institucionales para gráficos..."):
        chart_data = fetch_stock_data(ticker_input)

    if chart_data.empty:
        st.error(f"No se encontraron datos para {ticker_input}. Revisa el símbolo.")
        return

    # 2. Datos de Alpaca para lógica de trading (backtest, simulación, ejecución).
    with st.spinner("Descargando datos de Alpaca para trading..."):
        trading_data = fetch_trading_data_alpaca(ticker_input)

    # --- PROCESAMIENTO DE DATOS ---
    # Procesamos los datos para las visualizaciones.
    processed_chart_data = chart_data.reset_index()
    if pd.api.types.is_datetime64_any_dtype(processed_chart_data["Date"]):
        if processed_chart_data["Date"].dt.tz is not None:
            processed_chart_data["Date"] = processed_chart_data["Date"].dt.tz_localize(
                None
            )

    processed_chart_data = process_data(processed_chart_data, ma_window)
    processed_chart_data = calculate_support_resistance(processed_chart_data)
    processed_chart_data, _ = find_complex_patterns(processed_chart_data)

    # Procesamos los datos de Alpaca para el motor de trading.
    # Si Alpaca falla, usamos los de yfinance como fallback para no romper la app.
    if not trading_data.empty:
        processed_trading_data = process_data(trading_data.copy(), ma_window)
        processed_trading_data = calculate_support_resistance(processed_trading_data)
        processed_trading_data, _ = find_complex_patterns(processed_trading_data)
    else:
        st.warning(
            "No se pudieron obtener datos de Alpaca. Las simulaciones y backtesting usarán datos estándar como fallback."
        )
        processed_trading_data = processed_chart_data.copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Precio Cierre", f"${processed_chart_data['Close'].iloc[-1]:.2f}")
    m2.metric(
        "Retorno Diario", f"{processed_chart_data['Daily Return'].iloc[-1] * 100:.2f}%"
    )

    rsi_val = (
        processed_chart_data["RSI_14"].iloc[-1]
        if "RSI_14" in processed_chart_data.columns
        else 0.0
    )
    m3.metric("RSI 14", f"{rsi_val:.2f}")

    rel_vol_val = (
        processed_chart_data["Rel_Vol"].iloc[-1]
        if "Rel_Vol" in processed_chart_data.columns
        else 0.0
    )
    m4.metric("Volumen Rel.", f"{rel_vol_val:.2f}x")

    # Métricas adicionales de soporte/resistencia
    soporte_actual = processed_chart_data["Support_Level"].iloc[-1]
    resistencia_actual = processed_chart_data["Resistance_Level"].iloc[-1]
    precio_actual = processed_chart_data["Close"].iloc[-1]
    distancia_sop = ((precio_actual - soporte_actual) / soporte_actual) * 100

    st.caption(
        f"📍 Soporte: ${soporte_actual:.2f} | Resistencia: ${resistencia_actual:.2f} | Distancia Soporte: {distancia_sop:.2f}%"
    )

    t1, t2, t3, t4, t5, t6 = st.tabs(
        [
            "📈 Análisis Técnico",
            "🕯️ Patrones",
            "📊 Volumen y Riesgo",
            "🤖 Simulación",
            "📈 Backtesting",
            "📑 Data Bruta",
        ]
    )

    with t1:
        st.plotly_chart(
            create_candlestick_chart(processed_chart_data, ticker_input),
            use_container_width=True,
        )
        st.plotly_chart(
            create_moving_average_chart(processed_chart_data, ticker_input, ma_window),
            use_container_width=True,
        )
        st.plotly_chart(
            create_rsi_chart(processed_chart_data), use_container_width=True
        )

    with t2:
        st.subheader("🕯️ Detección de Patrones Complejos (Chartismo)")

        # Detectar patrones geométricos complejos
        processed_chart_data, complex_signals = find_complex_patterns(
            processed_chart_data
        )

        # Mostrar alertas de patrones detectados
        if complex_signals:
            st.markdown("### 📊 Patrones Detectados:")
            for pattern_name, pattern_signal in complex_signals.items():
                if pattern_name == "IHS":
                    st.success(
                        f"🚀 **ALERTA**: Se detectó un patrón **IHS (Hombro-Cabeza-Hombro Invertido)** en {ticker_input}"
                    )
                    st.info(
                        "💡 Este patrón sugiere un cambio de tendencia de **bajista a alcista**. Señal potencial de compra."
                    )
                elif pattern_name in ["DOJI", "HAMMER", "ENGULFING", "SHOOTINGSTAR"]:
                    st.info(
                        f"📍 Patrón de vela detectado: **{pattern_name}** - {pattern_signal}"
                    )
        else:
            st.info(
                "ℹ️ No se detectan patrones geométricos complejos en el período actual."
            )

        # Gráfico de patrones
        st.markdown("### 📈 Visualización de Patrones:")
        st.plotly_chart(
            create_patterns_only_chart(processed_chart_data, ticker_input),
            use_container_width=True,
        )

    with t3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                create_daily_returns_histogram(processed_chart_data),
                use_container_width=True,
            )
        with col_b:
            st.plotly_chart(
                create_volume_analysis_chart(processed_chart_data),
                use_container_width=True,
            )
        st.plotly_chart(
            create_volume_vs_close_scatter(processed_chart_data),
            use_container_width=True,
        )

    with t4:
        st.subheader("Simulación y Ejecución")
        col1, col2 = st.columns(2)

        with col1:
            st.info("### 🧪 Backtest Rápido")
            if st.button("🚀 Ejecutar Simulación", key="run_simulation"):
                ledger, position_qty, cash = run_simulation(
                    processed_trading_data, sl_input
                )
                st.success(f"Balance simulado final: ${cash:,.2f}")
                if ledger:
                    st.dataframe(
                        pd.DataFrame([vars(t) for t in ledger]),
                        use_container_width=True,
                    )
                else:
                    st.write("No se generaron trades durante el periodo analizado.")

        with col2:
            st.warning("### ⚡ Señales Alpaca")
            if not ALPACA_AVAILABLE:
                st.error(
                    "Alpaca no está disponible en este entorno. Instala alpaca-py para operar."
                )
            else:
                confirmar_envio = st.checkbox(
                    "Habilitar envío de órdenes a Alpaca", key="confirm_send"
                )
                if st.button(
                    "Enviar señal actual",
                    disabled=not confirmar_envio,
                    key="send_signal",
                ):
                    if api_key and secret_key:
                        try:
                            executor = AlpacaExecutor(api_key, secret_key, paper_mode)
                            engine = TradingEngine(stop_loss_pct=sl_input)
                            last_row = processed_trading_data.iloc[-1]
                            signal = engine.strategy(
                                last_row["Close"],
                                last_row["MA"],
                                last_row["Pattern_Detected"],
                            )
                            if signal == "BUY":
                                res = executor.place_order(ticker_input, 1, "BUY")
                                st.success(
                                    f"ORDEN ENVIADA: Compra de 1 {ticker_input}. ID: {res.id}"
                                )
                            elif signal == "SELL":
                                res = executor.place_order(ticker_input, 1, "SELL")
                                st.error(
                                    f"ORDEN ENVIADA: Venta de 1 {ticker_input}. ID: {res.id}"
                                )
                            else:
                                st.info(
                                    "No hay señal de entrada activa en este momento."
                                )
                        except Exception as e:
                            st.error(f"Error enviando orden a Alpaca: {e}")
                    else:
                        st.error("Ingresa tus credenciales Alpaca para enviar órdenes.")
                if not confirmar_envio:
                    st.caption("Activa la casilla para habilitar el botón de envío.")

    with t5:
        st.subheader("📈 Simulación Histórica de Rendimiento")
        bt_data, bt_metrics = run_backtest(
            processed_trading_data, initial_capital=10000
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Retorno Estrategia", f"{bt_metrics['Retorno Estrategia']:.2%}")
        m2.metric(
            "Retorno Mercado (Hold)", f"{bt_metrics['Retorno Mercado (Hold)']:.2%}"
        )
        m3.metric("Máximo Drawdown", f"{bt_metrics['Peor Caída (Max Drawdown)']:.2%}")

        st.plotly_chart(
            create_equity_curve_chart(bt_data, ticker_input), use_container_width=True
        )

    with t6:
        st.dataframe(processed_chart_data.tail(100), use_container_width=True)
