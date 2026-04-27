import streamlit as st


def render_paper_audit_tab():
    st.subheader("🧪 Auditoría de Transición: Paper a Real")
    st.markdown(
        "Métricas críticas para validar la robustez del algoritmo antes de exponer capital real."
    )

    st.divider()

    st.markdown("### 1. Rendimiento y Rentabilidad")
    c1, c2, c3 = st.columns(3)
    c1.metric("Profit Factor", "0.0", "Objetivo: > 1.8")
    c2.metric("Win Rate vs R:R", "0%", "Ej. 40% (R:R 1:3)")
    c3.metric("Net Profit", "$0.00", "Rentabilidad Neta")

    st.markdown("### 2. Riesgo y Consistencia")
    c4, c5, c6 = st.columns(3)
    c4.metric("Max Drawdown", "0%", "Objetivo: < 10-15%", delta_color="inverse")
    c5.metric("Sharpe Ratio", "0.0", "Objetivo: > 1.5")
    c6.metric(
        "Pérdidas Consecutivas Máx", "0", "Límite de estrés", delta_color="inverse"
    )

    st.markdown("### 3. Calidad de Ejecución (Fricción)")
    c7, c8 = st.columns(2)
    c7.metric("Slippage (Deslizamiento)", "$0.00", "Penalización aplicada")
    c8.metric("Trade Frequency", "0 / día", "Frecuencia moderada")

    st.divider()

    st.markdown("### 📋 Requisitos Técnicos de Certificación")
    st.checkbox(
        "Mínimo 3-6 meses de simulación bajo distintas condiciones (Alcista/Bajista/Lateral)",
        value=False,
    )
    st.checkbox(
        "Ejecución con datos de micro-estructura en tiempo real (Tick data, no solo backtest)",
        value=False,
    )
    st.checkbox(
        "Integración estricta de fricción (Comisiones + Spreads variables del broker)",
        value=False,
    )

    if st.button("Evaluar Transición a Real", width="stretch", type="primary"):
        st.error(
            "🔴 CERTIFICACIÓN RECHAZADA: El algoritmo no cumple con el periodo mínimo de prueba o métricas de Sharpe/Profit Factor."
        )
