import streamlit as st
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from src.data_fetcher import fetch_stock_data


def run_mean_reversion_backtest(df, initial_capital=10000):
    """
    Backtest de estrategia de Reversión a la Media (Volatility + ATR).
    Diseñado originalmente para la estructura del sector energía.
    """
    data = df.copy()

    # 1. Calcular Indicadores
    data.ta.bbands(length=20, std=2, append=True)
    data.ta.rsi(length=14, append=True)
    data.ta.sma(length=200, append=True)
    data.ta.atr(length=14, append=True)

    # 2. Búsqueda dinámica de columnas (evita errores si pandas_ta cambia nombres)
    try:
        bb_lower = [c for c in data.columns if "BBL" in c][0]
        bb_upper = [c for c in data.columns if "BBU" in c][0]
        sma_200 = [c for c in data.columns if "SMA_200" in c][0]
        rsi_14 = [c for c in data.columns if "RSI_14" in c][0]
        atr_14 = [c for c in data.columns if "ATRr_14" in c][0]
    except IndexError:
        return data, []  # Fallback de seguridad

    capital = initial_capital
    position = 0
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    trade_log = []

    data["Equity"] = capital

    # 3. Motor de Simulación (Inicia en 200 para tener la SMA cargada)
    for i in range(200, len(data)):
        current_price = data["Close"].iloc[i]
        current_date = data["Date"].iloc[i]

        # --- Evaluar Salidas ---
        if position > 0:
            if current_price <= stop_loss:
                # Stop Loss Hit
                capital += position * stop_loss  # Retornamos el capital a la cuenta
                ret = ((stop_loss - entry_price) / entry_price) * 100
                trade_log.append(
                    {"Date": current_date, "Type": "SL 🔴", "Return %": round(ret, 2)}
                )
                position = 0

            elif (
                current_price >= take_profit or current_price >= data[bb_upper].iloc[i]
            ):
                # Take Profit Hit (Target dinámico o Banda Superior)
                capital += position * current_price
                ret = ((current_price - entry_price) / entry_price) * 100
                trade_log.append(
                    {"Date": current_date, "Type": "TP 🟢", "Return %": round(ret, 2)}
                )
                position = 0

        # --- Evaluar Entradas ---
        elif position == 0:
            if (
                current_price > data[sma_200].iloc[i]
                and current_price < data[bb_lower].iloc[i]
                and data[rsi_14].iloc[i] < 30
            ):

                # Gestión de Riesgo Institucional: 1% de la cuenta actual
                risk_amount = capital * 0.01
                atr_val = data[atr_14].iloc[i]

                # SL Dinámico basado en volatilidad (1.5x ATR)
                sl_distance = 1.5 * atr_val
                stop_loss = current_price - sl_distance
                take_profit = current_price + (sl_distance * 3)  # Asimetría 1:3

                # Sizing de posición
                shares_to_buy = risk_amount / sl_distance
                invested_amount = shares_to_buy * current_price

                if invested_amount <= capital:
                    position = shares_to_buy
                    capital -= invested_amount
                    entry_price = current_price

        # --- Actualizar Equidad Diaria ---
        data.at[data.index[i], "Equity"] = capital + (
            position * current_price if position > 0 else 0
        )

    return data, trade_log


def render_tear_sheet_tab(ticker):
    st.subheader(f"📈 Quant Tear Sheet: Reversión a la Media ({ticker})")
    st.markdown(
        "Auditoría cuantitativa del algoritmo basado en **SMA 200 + BB + RSI 30 + ATR Sizing**."
    )

    with st.spinner("Compilando simulación histórica (requiere 2 años de datos)..."):
        # Extraemos suficientes datos para que la SMA 200 tenga espacio para operar
        df = fetch_stock_data(ticker, period_days=1000)

        if df.empty or len(df) < 250:
            st.warning(
                "No hay suficientes datos históricos para ejecutar un backtest de 200 periodos."
            )
            return

        initial_cap = 10000.0
        backtest_data, trades = run_mean_reversion_backtest(
            df, initial_capital=initial_cap
        )

        final_equity = backtest_data["Equity"].iloc[-1]
        net_profit = ((final_equity - initial_cap) / initial_cap) * 100

        # Calcular Win Rate
        total_trades = len(trades)
        winning_trades = len([t for t in trades if "TP" in t["Type"]])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # --- PANEL DE MÉTRICAS ---
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Capital Final", f"${final_equity:,.2f}", f"{net_profit:.2f}%")
        c2.metric("Total Trades", total_trades)
        c3.metric("Win Rate", f"{win_rate:.1f}%", "Objetivo: >35% con R:R 1:3")

        # Max Drawdown aproximado sobre la curva de Equity
        rolling_max = backtest_data["Equity"].cummax()
        drawdown = (backtest_data["Equity"] - rolling_max) / rolling_max
        max_dd = drawdown.min() * 100
        c4.metric("Max Drawdown", f"{max_dd:.2f}%", delta_color="inverse")

        # --- CURVA DE RENDIMIENTO (EQUITY CURVE) ---
        fig = go.Figure()

        # Línea Base (Capital Inicial)
        fig.add_hline(
            y=initial_cap,
            line_dash="dot",
            line_color="gray",
            annotation_text="Capital Base",
        )

        # Curva de Estrategia
        fig.add_trace(
            go.Scatter(
                x=backtest_data["Date"],
                y=backtest_data["Equity"],
                name="Estrategia",
                line=dict(color="#00FFA3", width=2),
                fill="tozeroy",
                fillcolor="rgba(0, 255, 163, 0.1)",
            )
        )

        fig.update_layout(
            title="Curva de Crecimiento de Capital (Compound Equity)",
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis_title="Capital ($)",
            xaxis_title="Fecha",
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- BITÁCORA DE TRANSACCIONES ---
        if trades:
            with st.expander("📓 Registro de Operaciones (Trade Log)"):
                st.dataframe(
                    pd.DataFrame(trades).set_index("Date"), use_container_width=True
                )
