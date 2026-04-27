import streamlit as st


def render_premarket_tab(ticker):
    st.subheader(f"☀️ Inteligencia Pre-Market: {ticker}")
    st.markdown("Auditoría de liquidez antes de la campana (08:00 AM - 09:30 AM EST)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📰 Catalizadores Macro")
        st.checkbox("Guerras / Conflictos Geopolíticos (Energía/Oro)")
        st.checkbox("Decisiones de Tasas de la FED (Índices)")
        st.checkbox("Datos de Inflación CPI/PPI (Volatilidad)")
    with col2:
        st.markdown("### 📊 Gaps de Apertura")
        st.text_input("Ingresa el cierre de ayer:")
        st.caption("Los algoritmos tienden a rellenar gaps en la primera hora.")
