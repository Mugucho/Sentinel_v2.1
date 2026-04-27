# Ejemplos de Integración en el Software

## Ejemplo 1: Tab Market Lab Mejorado

```python
# En views/tab_market_lab.py

import streamlit as st
from src.visualizations import (
    create_candlestick_chart,
    create_moving_average_chart,
    create_rsi_chart,
    create_macd_chart,  # NUEVO
    create_volume_analysis_chart,
    create_price_performance_chart,  # NUEVO
    score_stock  # NUEVO
)

def render_market_lab_tab(ticker):
    # ... código existente ...
    
    with t1:  # Tab "Análisis Técnico"
        st.plotly_chart(
            create_candlestick_chart(processed_chart_data, ticker_input),
            use_container_width=True,
        )
        
        # NUEVO: Comparación de promedios móviles
        st.plotly_chart(
            create_moving_average_chart(processed_chart_data, ticker_input, ma_window),
            use_container_width=True,
        )
        
        # NUEVO: Mostrar MACD en dos columnas con RSI
        col_rsi, col_macd = st.columns(2)
        with col_rsi:
            st.plotly_chart(create_rsi_chart(processed_chart_data), use_container_width=True)
        with col_macd:
            st.plotly_chart(create_macd_chart(processed_chart_data), use_container_width=True)
    
    # NUEVO: Tab de Performance
    with st.tabs(["📊 Performance Acumulado"]):
        st.plotly_chart(
            create_price_performance_chart(processed_chart_data, ticker_input),
            use_container_width=True,
        )
    
    # NUEVO: Score del Stock
    with st.expander("🎯 Análisis de Calidad (Stock Score)"):
        score, signals = score_stock(processed_chart_data)
        
        # Mostrar score con indicador visual
        col1, col2, col3 = st.columns(3)
        with col1:
            color = "🟢" if score >= 6 else "🟡" if score >= 4 else "🔴"
            st.metric("Score de Calidad", f"{color} {score}/8")
        
        with col2:
            st.metric("Recomendación", "COMPRA" if score >= 6 else "HOLD" if score >= 4 else "VENTA")
        
        with col3:
            st.metric("Confianza", f"{(score/8)*100:.0f}%")
        
        st.markdown("### Señales Técnicas:")
        for signal in signals:
            st.write(signal)
```

---

## Ejemplo 2: Dashboard de Screening Multi-Ticker

```python
# Nuevo archivo: views/tab_stock_scanner.py

import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.visualizations import (
    create_stock_scoring_chart,
    score_stock,
    calculate_rsi,
    calculate_macd
)

def render_stock_scanner():
    st.subheader("📊 Stock Scanner - Screening Automático")
    
    # Input de tickers a analizar
    tickers_input = st.text_area(
        "Ingresa tickers separados por coma (ej: AAPL,MSFT,GOOGL)",
        value="AAPL,MSFT,GOOGL,TSLA,AMZN"
    ).upper().split(",")
    
    tickers = [t.strip() for t in tickers_input if t.strip()]
    
    if st.button("Analizar Tickers"):
        progress_bar = st.progress(0)
        scores_data = []
        
        for idx, ticker in enumerate(tickers):
            try:
                # Obtener y procesar datos
                data = fetch_stock_data(ticker)
                data = process_data(data.reset_index(), ma_window=50)
                data = calculate_rsi(data)
                data = calculate_macd(data)
                
                # Calcular score
                score, _ = score_stock(data)
                scores_data.append((ticker, score))
                
            except Exception as e:
                st.warning(f"No se pudo procesar {ticker}: {e}")
            
            progress_bar.progress((idx + 1) / len(tickers))
        
        # Mostrar resultados
        if scores_data:
            st.plotly_chart(
                create_stock_scoring_chart(scores_data),
                use_container_width=True
            )
            
            # Tabla de resultados
            df_results = pd.DataFrame(scores_data, columns=['Ticker', 'Score'])
            df_results = df_results.sort_values('Score', ascending=False)
            df_results['Recomendación'] = df_results['Score'].apply(
                lambda x: '🟢 COMPRA' if x >= 6 else '🟡 HOLD' if x >= 4 else '🔴 VENTA'
            )
            
            st.dataframe(df_results, use_container_width=True)
```

---

## Ejemplo 3: Análisis Comparativo de Correlaciones

```python
# En views/tab_correlations.py

import streamlit as st
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.visualizations import create_correlation_heatmap

def render_correlations_tab():
    st.subheader("🔗 Matriz de Correlación")
    
    # Seleccionar tickers a comparar
    tickers = st.multiselect(
        "Selecciona activos para análisis de correlación",
        options=["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NFLX", "META"],
        default=["AAPL", "MSFT", "GOOGL"]
    )
    
    if len(tickers) >= 2:
        data_dict = {}
        
        for ticker in tickers:
            try:
                data = fetch_stock_data(ticker)
                data = process_data(data.reset_index(), ma_window=50)
                data_dict[ticker] = data
            except Exception as e:
                st.error(f"Error obteniendo datos para {ticker}: {e}")
        
        if data_dict:
            st.plotly_chart(
                create_correlation_heatmap(data_dict),
                use_container_width=True
            )
            
            # Interpretación de correlaciones
            st.info(
                """
                **Interpretación:**
                - **Verde oscuro:** Correlación positiva fuerte (0.7 a 1.0) - se mueven juntos al alza
                - **Amarillo:** Correlación neutral (0.0 a 0.3) - movimientos independientes
                - **Rojo:** Correlación negativa (-0.7 a -1.0) - se mueven en direcciones opuestas
                
                **Uso para trading:**
                - Correlación positiva → Riesgo de diversificación reducido
                - Correlación negativa → Bueno para hedging
                """
            )
    else:
        st.warning("Selecciona al menos 2 tickers para ver la correlación")
```

---

## Ejemplo 4: Integración en Dashboard Principal

```python
# En dashboard.py - Agregar estas funciones

import streamlit as st
from src.visualizations import create_stock_scoring_chart, create_correlation_heatmap

# En la sección de métricas
st.markdown("### 🏆 Top Stocks por Score")

# Suponiendo que tienes un análisis previo
tickers_analysis = [
    ("AAPL", 7),
    ("MSFT", 6),
    ("GOOGL", 5),
    ("TSLA", 4),
    ("META", 3),
]

col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(
        create_stock_scoring_chart(tickers_analysis),
        use_container_width=True
    )

with col2:
    st.markdown("### Leyenda de Scores")
    st.markdown("- **7-8:** 🟢 Compra fuerte")
    st.markdown("- **5-6:** 🟡 Compra moderada")
    st.markdown("- **3-4:** 🟠 Hold/Revisar")
    st.markdown("- **0-2:** 🔴 Venta/Evitar")
```

---

## Ejemplo 5: Alerta de Cambios de Tendencia

```python
# Función auxiliar para alertas
from src.visualizations import calculate_rsi, calculate_macd

def check_trading_signals(data):
    """Detecta cambios de tendencia y genera alertas"""
    
    data = calculate_rsi(data)
    data = calculate_macd(data)
    
    signals = []
    
    # Señal RSI
    rsi_actual = data['RSI_14'].iloc[-1]
    if rsi_actual > 70:
        signals.append(("RSI", "🔴 Sobrecomprado (>70)", "warning"))
    elif rsi_actual < 30:
        signals.append(("RSI", "🟢 Sobrevendido (<30)", "success"))
    
    # Señal MACD
    if len(data) > 1:
        macd_prev = data['MACD'].iloc[-2]
        macd_curr = data['MACD'].iloc[-1]
        
        if macd_prev < 0 and macd_curr > 0:
            signals.append(("MACD", "🟢 Cruce positivo", "success"))
        elif macd_prev > 0 and macd_curr < 0:
            signals.append(("MACD", "🔴 Cruce negativo", "error"))
    
    return signals

# Usar en Streamlit
def render_alerts(data, ticker):
    signals = check_trading_signals(data)
    
    if signals:
        st.markdown("### ⚠️ Señales Activas")
        for indicator, message, severity in signals:
            st.markdown(f"**{indicator}:** {message}", unsafe_allow_html=True)
```

---

## Migración de Código Existente

### Antes:
```python
fig = create_candlestick_chart(processed_chart_data, ticker_input)
st.plotly_chart(fig)
```

### Después (idéntico - totalmente compatible):
```python
fig = create_candlestick_chart(processed_chart_data, ticker_input)
st.plotly_chart(fig)
```

**¡No requiere cambios en el código existente!** Las mejoras son internas.

---

## Nuevas Funcionalidades Opcionales a Agregar

Si quieres agregar más funcionalidades, aquí están las líneas sugeridas:

1. **Exportar análisis a PDF:**
   ```python
   from reportlab.pdfgen import canvas
   # Generar reporte con gráficos y scores
   ```

2. **Almacenar histórico de scores:**
   ```python
   # Guardar scores en CSV/BD para tracking histórico
   df_history = pd.read_csv('scores_history.csv')
   ```

3. **Alertas por email:**
   ```python
   # Si score cruza threshold, enviar alerta
   ```

---

**Próximos pasos sugeridos:**
1. Agregar las nuevas funciones al tab_market_lab.py existente
2. Crear un nuevo tab de Stock Scanner
3. Integrar alertas automáticas
4. Agregar exportación de análisis
