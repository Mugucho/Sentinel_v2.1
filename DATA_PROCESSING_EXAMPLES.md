# Ejemplos de Uso - process_data Mejorada

## Ejemplo 1: Análisis Básico

```python
import streamlit as st
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data

# Obtener y procesar datos
ticker = "AAPL"
data = fetch_stock_data(ticker)
processed = process_data(data, ma_window=50)

# Ver los últimos 5 días con indicadores
st.dataframe(processed[['Date', 'Close', 'MA', 'RSI_14', 'Volatility', 'Pattern_Detected']].tail())

# Estadísticas de patrones
st.write("### Conteo de Patrones Detectados")
st.bar_chart(processed['Pattern_Detected'].value_counts())
```

---

## Ejemplo 2: Filtrado por Patrón

```python
from src.data_processing import process_data

# Procesar datos
processed = process_data(data)

# Filtrar por patrones específicos
hammer_signals = processed[processed['Pattern_Detected'] == 'HAMMER']
bullish_signals = processed[processed['Pattern_Detected'] == 'BULL']
engulfing_signals = processed[processed['Pattern_Detected'] == 'ENGULFING']

print(f"Martillos detectados: {len(hammer_signals)}")
print(f"Patrones alcistas: {len(bullish_signals)}")
print(f"Patrones envolventes: {len(engulfing_signals)}")

# Mostrar detalles
if len(hammer_signals) > 0:
    print("\n=== Últimas Señales de Martillo ===")
    print(hammer_signals[['Date', 'Close', 'RSI_14', 'Volume']].tail(3))
```

---

## Ejemplo 3: Análisis Técnico Completo

```python
import streamlit as st
from src.data_processing import process_data
from src.visualizations import create_candlestick_chart

ticker = "MSFT"
data = fetch_stock_data(ticker)
processed = process_data(data, ma_window=50)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

latest = processed.iloc[-1]

with col1:
    st.metric(
        "Precio Cierre",
        f"${latest['Close']:.2f}",
        f"{latest['Daily Return']*100:.2f}%"
    )

with col2:
    st.metric("RSI 14", f"{latest['RSI_14']:.2f}", "")

with col3:
    st.metric("Volatilidad", f"{latest['Volatility']*100:.2f}%", "")

with col4:
    st.metric("Vol. Relativo", f"{latest['Rel_Vol']:.2f}x", "")

# Patrón actual
st.markdown(f"### Patrón Detectado: **{latest['Pattern_Detected']}**")

# Gráfico
st.plotly_chart(
    create_candlestick_chart(processed, ticker),
    use_container_width=True
)
```

---

## Ejemplo 4: Scanning de Patrones Múltiples

```python
import streamlit as st
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data

tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
pattern_summary = []

with st.spinner("Analizando patrones..."):
    for ticker in tickers:
        try:
            data = fetch_stock_data(ticker)
            processed = process_data(data, ma_window=50)
            
            latest = processed.iloc[-1]
            
            # Contar patrones en últimas 10 barras
            recent_10 = processed.tail(10)
            pattern_counts = recent_10['Pattern_Detected'].value_counts()
            
            pattern_summary.append({
                'Ticker': ticker,
                'Precio': f"${latest['Close']:.2f}",
                'RSI': f"{latest['RSI_14']:.2f}",
                'Patrón Actual': latest['Pattern_Detected'],
                'Patrones (10d)': len(recent_10[recent_10['Pattern_Detected'] != 'NEUTRAL'])
            })
        except Exception as e:
            st.error(f"Error con {ticker}: {e}")

# Mostrar tabla
import pandas as pd
df_summary = pd.DataFrame(pattern_summary)
st.dataframe(df_summary, use_container_width=True)
```

---

## Ejemplo 5: Búsqueda de Confluencias

```python
def find_confluence_signals(data, processed):
    """Busca confluencias de múltiples indicadores"""
    signals = []
    
    for idx in range(1, len(processed)):
        row = processed.iloc[idx]
        
        # Condiciones para señal alcista confluente
        is_bullish_pattern = row['Pattern_Detected'] in ['BULL', 'HAMMER']
        is_oversold = row['RSI_14'] < 30
        is_above_ma = row['Close'] > row['MA']
        high_volume = row['Rel_Vol'] > 1.2
        
        confluence_score = sum([is_bullish_pattern, is_oversold, is_above_ma, high_volume])
        
        if confluence_score >= 3:  # Al menos 3 señales confluentes
            signals.append({
                'Date': row['Date'],
                'Price': row['Close'],
                'Pattern': row['Pattern_Detected'],
                'RSI': row['RSI_14'],
                'Rel_Vol': row['Rel_Vol'],
                'Confluence_Score': confluence_score
            })
    
    return signals

# Usar la función
processed = process_data(fetch_stock_data("AAPL"))
confluences = find_confluence_signals(data, processed)

if confluences:
    st.success(f"🎯 Se encontraron {len(confluences)} señales confluentes")
    
    for signal in confluences[-5:]:  # Mostrar últimas 5
        st.write(f"""
        **{signal['Date']}**
        - Precio: ${signal['Price']:.2f}
        - Patrón: {signal['Pattern']}
        - RSI: {signal['RSI']:.2f}
        - Vol. Rel: {signal['Rel_Vol']:.2f}x
        - Score: {signal['Confluence_Score']}/4
        """)
```

---

## Ejemplo 6: Análisis de Volatilidad

```python
from src.data_processing import process_data
import streamlit as st

ticker = "TSLA"
processed = process_data(fetch_stock_data(ticker))

# Estadísticas de volatilidad
vol_mean = processed['Volatility'].mean()
vol_std = processed['Volatility'].std()
vol_current = processed['Volatility'].iloc[-1]

st.metric("Volatilidad Actual", f"{vol_current*100:.2f}%")
st.metric("Volatilidad Promedio (20d)", f"{vol_mean*100:.2f}%")
st.metric("Desv. Estándar Vol", f"{vol_std*100:.2f}%")

# Clasificación
if vol_current > vol_mean + vol_std:
    st.warning("⚠️ Volatilidad ALTA")
elif vol_current > vol_mean:
    st.info("📊 Volatilidad MODERADA")
else:
    st.success("✅ Volatilidad BAJA")

# Gráfico de volatilidad
st.line_chart(processed[['Date', 'Volatility']].set_index('Date'))
```

---

## Ejemplo 7: Integración en Dashboard Completo

```python
import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.visualizations import create_candlestick_chart, create_rsi_chart

st.title("Dashboard de Análisis Técnico")

# Inputs
ticker = st.text_input("Ticker", "AAPL").upper()
ma_window = st.slider("Ventana SMA", 10, 200, 50, 10)

if ticker:
    # Procesar datos
    data = fetch_stock_data(ticker)
    processed = process_data(data, ma_window=ma_window)
    
    # Resumen
    latest = processed.iloc[-1]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Precio", f"${latest['Close']:.2f}")
    with col2:
        st.metric("RSI", f"{latest['RSI_14']:.2f}")
    with col3:
        st.metric("Vol Rel", f"{latest['Rel_Vol']:.2f}x")
    with col4:
        st.metric("Volatilidad", f"{latest['Volatility']*100:.2f}%")
    with col5:
        st.metric("Patrón", latest['Pattern_Detected'])
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["Candlestick", "RSI", "Patrones"])
    
    with tab1:
        st.plotly_chart(
            create_candlestick_chart(processed, ticker),
            use_container_width=True
        )
    
    with tab2:
        st.plotly_chart(
            create_rsi_chart(processed),
            use_container_width=True
        )
    
    with tab3:
        pattern_counts = processed['Pattern_Detected'].value_counts()
        st.bar_chart(pattern_counts)
    
    # Tabla de datos
    st.markdown("### Datos Procesados")
    st.dataframe(
        processed[['Date', 'Close', 'MA', 'RSI_14', 'Rel_Vol', 'Pattern_Detected']].tail(20),
        use_container_width=True
    )
```

---

## Ejemplo 8: Exportar Análisis a CSV

```python
import pandas as pd
from datetime import datetime

ticker = "AAPL"
processed = process_data(fetch_stock_data(ticker))

# Seleccionar columnas relevantes
export_df = processed[[
    'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
    'MA', 'RSI_14', 'Volatility', 'Rel_Vol', 'Pattern_Detected'
]].copy()

# Guardar
filename = f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
export_df.to_csv(filename, index=False)

print(f"Análisis exportado a: {filename}")
print(f"Total de barras: {len(export_df)}")
print(f"\nPatrones detectados:")
print(export_df['Pattern_Detected'].value_counts())
```

---

## Configuración Recomendada

### Para análisis intradiario (corto plazo):
```python
processed = process_data(data, ma_window=20)
```

### Para análisis swing trading (medio plazo):
```python
processed = process_data(data, ma_window=50)
```

### Para análisis de tendencia (largo plazo):
```python
processed = process_data(data, ma_window=200)
```

---

## Notas de Performance

- La función es rápida incluso para datasets grandes (10,000+ barras)
- El manejo de errores es robusto
- Compatible con todos los timeframes
- No requiere conexión a internet después del primer fetch

---

**Última actualización:** 2026-04-25
**Versión:** 2.1
