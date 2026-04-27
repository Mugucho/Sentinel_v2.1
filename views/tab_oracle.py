import streamlit as st
from src.oracle import get_market_sentiment


def render_oracle_tab(ticker):
    st.subheader("🔮 Oráculo de Sentimiento de Mercado")
    st.markdown(
        """
    El Oráculo analiza las noticias financieras más recientes usando procesamiento de lenguaje natural (NLP)
    para determinar el sentimiento general del mercado hacia un activo específico.
    """
    )

    if st.button("🔍 Consultar Sentimiento Actual", use_container_width=True):
        with st.spinner("Analizando titulares de noticias..."):
            sentimiento, score = get_market_sentiment(ticker)

            if sentimiento != 0 or score != "Falta API Key":  # Si la función retorna datos válidos
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 📊 Sentimiento Detectado")
                    if "Bullish" in score:
                        st.success(f"🟢 {score}")
                    elif "Bearish" in score:
                        st.error(f"🔴 {score}")
                    else:
                        st.info(f"🟡 {score}")

                with col2:
                    st.markdown("### 📈 Score de Polaridad")
                    st.metric("Polaridad", f"{sentimiento:.3f}")
                    if sentimiento > 0.15:
                        st.caption("Sentimiento positivo fuerte detectado")
                    elif sentimiento < -0.15:
                        st.caption("Sentimiento negativo fuerte detectado")
                    else:
                        st.caption("Sentimiento neutral/mixto")

                st.markdown("### 📋 Información Técnica")
                st.caption(
                    """
                    - **Bullish (🟢)**: Polaridad > 0.15 - Sentimiento positivo
                    - **Bearish (🔴)**: Polaridad < -0.15 - Sentimiento negativo
                    - **Neutral (🟡)**: Polaridad entre -0.15 y 0.15 - Sentimiento equilibrado
                    """
                )
            else:
                st.warning("No se pudo obtener el sentimiento. Verifica tu API Key de Finnhub.")

    st.divider()
    st.info(
        "💡 **Arquitectura del Motor:** El algoritmo analiza noticias recientes usando NLP para determinar el sentimiento del mercado hacia el activo."
    )
