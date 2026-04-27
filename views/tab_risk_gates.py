import streamlit as st
from src.notifier import send_telegram_alert
from src.risk_management import drawdown_gate, exposure_gate, reconciliation_gate
import os

# Simulación de conexión Alpaca (en producción sería real)
try:
    from alpaca.trading.client import TradingClient

    tc = TradingClient(
        os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True
    )
except:
    tc = None


def render_risk_gates_tab():
    st.subheader("🛡️ Risk Management Pipeline")
    st.markdown(
        "Sistema de tres compuertas de seguridad que protegen el capital institucional."
    )

    if tc:
        try:
            account = tc.get_account()
            # Compuerta 1: Drawdown
            is_safe, daily_pl = drawdown_gate(account, max_drawdown_pct=-0.02)

            if not is_safe:
                st.error(
                    f"🛑 BLOQUEO DE SEGURIDAD: Pérdida diaria {daily_pl:.2%}. Operativa suspendida."
                )
            else:
                st.success(f"✅ Drawdown Gate OK (P/L Diario: {daily_pl:.2%})")
                # Compuertas 2 y 3: Exposición y Reconciliación
                precio_actual = st.number_input("Precio Actual del Activo", value=100.0)
                max_allowed_qty = exposure_gate(
                    account, precio_actual, max_portfolio_pct=0.10
                )
                ticker = st.text_input("Ticker para Reconciliación", "AAPL").upper()
                current_position = reconciliation_gate(tc, ticker)

                st.info(
                    f"🛡️ Exposure Gate: Límite sugerido de **{max_allowed_qty}** acciones."
                )
                if current_position > 0:
                    st.warning(
                        f"🔄 Reconciliation Gate: Ya posees **{current_position}** acciones."
                    )
                else:
                    st.info("🔄 Reconciliation Gate: Posición limpia.")

        except Exception as e:
            st.error(f"Error conectando con Alpaca: {e}")
    else:
        st.warning("Conexión Alpaca no disponible. Mostrando modo simulado.")

        # Modo simulado
        st.markdown("### 🔧 Modo Simulado (Sin Conexión Alpaca)")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Drawdown Gate**")
            sim_dd = st.slider("P/L Diario Simulado", -0.05, 0.05, 0.01)
            if sim_dd >= -0.02:
                st.success("✅ Drawdown OK")
            else:
                st.error("🛑 Drawdown Excedido")

        with col2:
            st.markdown("**Exposure Gate**")
            sim_price = st.number_input("Precio Simulado", value=100.0)
            sim_equity = st.number_input("Equity Simulado", value=10000.0)
            max_qty = int((sim_equity * 0.10) / sim_price)
            st.info(f"Límite: {max_qty} acciones")

        with col3:
            st.markdown("**Reconciliation Gate**")
            sim_position = st.number_input("Posición Actual", value=0)
            if sim_position == 0:
                st.success("✅ Posición Limpia")
            else:
                st.warning(f"⚠️ Posición abierta: {sim_position}")
