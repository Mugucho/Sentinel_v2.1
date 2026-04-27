import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.macro_analysis import get_historical_macro_events, create_macro_chart


def render_macro_tab(ticker):
    st.subheader("🌍 Análisis de Impacto Geopolítico y Macro")
    st.caption(
        "Investiga cómo los eventos globales (decisiones de la FED, conflictos, inflación) afectaron el precio de "
        + ticker
        + " en periodos específicos."
    )

    # 1. Obtención de datos históricos para la base del gráfico
    with st.spinner("Cargando histórico macro..."):
        data = fetch_stock_data(ticker, period_days=730)  # 2 años para contexto amplio

    if data.empty:
        st.warning("No hay datos suficientes para realizar el análisis macro.")
        return

    # 2. Selectores de Fecha
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        start_f = st.date_input("Fecha Inicio", value=data["Date"].iloc[0])
    with c_f2:
        end_f = st.date_input("Fecha Fin", value=data["Date"].iloc[-1])

    # 3. Sincronización con NewsAPI (vía macro_analysis.py)
    if st.button("Sincronizar Datos Macro", use_container_width=True):
        with st.spinner("Correlacionando eventos económicos y titulares..."):

            # Filtrado temporal para el zoom interactivo
            mask = (data["Date"] >= pd.to_datetime(start_f)) & (
                data["Date"] <= pd.to_datetime(end_f)
            )
            filtered_data = data.loc[mask]

            # Llamada al motor de análisis que ya tienes en src/
            macro_events = get_historical_macro_events(ticker, start_f, end_f)

            if macro_events:
                # Generación del gráfico con hitos (Markers dorados)
                st.plotly_chart(
                    create_macro_chart(filtered_data, macro_events, ticker),
                    use_container_width=True,
                )

                # Listado descriptivo de los hitos encontrados
                st.markdown("### 📝 Hitos Identificados")
                for e in macro_events:
                    with st.expander(f"📅 {e['Date']} - {e['Title']}"):
                        st.write(e["Description"])
            else:
                st.warning(
                    "No se hallaron hitos específicos en el rango seleccionado. Intenta ampliar las fechas o verifica tu NEWS_API_KEY."
                )

    st.divider()
    st.info(
        "💡 **Tip:** Esta herramienta cruza la acción del precio con la NewsAPI para detectar por qué ocurrieron movimientos inusuales de volumen o precio."
    )
