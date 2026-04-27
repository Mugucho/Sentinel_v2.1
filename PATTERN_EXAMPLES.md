# Ejemplos de Uso - Detección de Patrones Complejos

## Ejemplo 1: Uso Básico en Market Lab

El código se ejecuta automáticamente cuando abres la pestaña "Patrones":

```python
# En views/tab_market_lab.py (ya integrado)

with t2:  # Pestaña "🕯️ Patrones"
    st.subheader("🕯️ Detección de Patrones Complejos (Chartismo)")
    
    # Esta línea detecta automáticamente todos los patrones
    processed_chart_data, complex_signals = find_complex_patterns(processed_chart_data)
    
    # Muestra las alertas detectadas
    if complex_signals:
        st.markdown("### 📊 Patrones Detectados:")
        for pattern_name, pattern_signal in complex_signals.items():
            if pattern_name == "IHS":
                st.success(f"🚀 **ALERTA**: Se detectó un patrón **IHS** en {ticker_input}")
                st.info("💡 Este patrón sugiere reversión de bajista a alcista.")
            # ... más patrones
```

**Output en Streamlit:**
```
🕯️ Detección de Patrones Complejos (Chartismo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Patrones Detectados:

🚀 ALERTA: Se detectó un patrón IHS (Hombro-Cabeza-Hombro Invertido) en AAPL
💡 Este patrón sugiere un cambio de tendencia de bajista a alcista. Señal potencial de compra.

📈 Visualización de Patrones:
[Gráfico con patrones marcados]
```

---

## Ejemplo 2: Uso Independiente

Si quieres usar la detección de patrones en otra parte del código:

```python
import streamlit as st
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.pattern_recognition import find_complex_patterns, detect_ihs_pattern
from src.visualizations import create_patterns_only_chart

ticker = "AAPL"
data = fetch_stock_data(ticker)
data = process_data(data.reset_index(), ma_window=50)

# Detectar todos los patrones
data, signals = find_complex_patterns(data)

# Mostrar resultados
st.write(f"**Patrones encontrados:** {len(signals)}")
for pattern, description in signals.items():
    st.write(f"- {pattern}: {description}")

# Visualizar
st.plotly_chart(create_patterns_only_chart(data, ticker))
```

---

## Ejemplo 3: Detección Específica de IHS

```python
from src.pattern_recognition import detect_ihs_pattern
import pandas as pd

# Después de procesar datos
ihs_patterns = detect_ihs_pattern(df)

if ihs_patterns:
    st.success(f"🚀 Se detectaron {len(ihs_patterns)} patrones IHS")
    
    # Mostrar detalles de cada patrón
    for idx, pattern in enumerate(ihs_patterns):
        st.markdown(f"""
        **Patrón IHS #{idx+1}**
        - Índice: {pattern['index']}
        - Hombro Izquierdo: ${pattern['left_shoulder']:.2f}
        - Cabeza: ${pattern['head']:.2f}
        - Hombro Derecho: ${pattern['right_shoulder']:.2f}
        - Profundidad: {pattern['depth']:.2f}%
        """)
else:
    st.info("ℹ️ No se detectaron patrones IHS en el período")
```

**Output:**
```
🚀 Se detectaron 1 patrones IHS

Patrón IHS #1
- Índice: 45
- Hombro Izquierdo: $150.25
- Cabeza: $145.30
- Hombro Derecho: $150.10
- Profundidad: 8.5%
```

---

## Ejemplo 4: Análisis Combinado (Patrón + Indicadores)

```python
from src.pattern_recognition import find_complex_patterns
from src.visualizations import (
    create_rsi_chart,
    create_macd_chart,
    score_stock
)

# Procesar datos
data, signals = find_complex_patterns(data)

# Mostrar hallazgos principales
col1, col2, col3 = st.columns(3)

with col1:
    if "IHS" in signals:
        st.success("🚀 IHS Detectado")
    else:
        st.info("➖ Sin IHS")

with col2:
    score, _ = score_stock(data)
    st.metric("Stock Score", f"{score}/8")

with col3:
    rsi = data['RSI_14'].iloc[-1]
    if rsi < 30:
        st.warning("📉 Sobreventa")
    elif rsi > 70:
        st.warning("📈 Sobrecompra")
    else:
        st.info("⚖️ RSI Normal")

# Gráficos
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(create_rsi_chart(data), use_container_width=True)
with col_right:
    st.plotly_chart(create_macd_chart(data), use_container_width=True)

# Señal de confirmación
if "IHS" in signals and data['RSI_14'].iloc[-1] < 30:
    st.success("""
    ✅ **Señal de Compra Confirmada**
    - IHS Detectado + Sobreventa (RSI < 30)
    - Potencial de reversión significativo
    """)
```

**Output:**
```
🚀 IHS Detectado    | Stock Score: 6/8    | 📉 Sobreventa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[RSI Chart]                         [MACD Chart]

✅ Señal de Compra Confirmada
- IHS Detectado + Sobreventa (RSI < 30)
- Potencial de reversión significativo
```

---

## Ejemplo 5: Alertas en Tiempo Real

```python
import streamlit as st
from datetime import datetime

# Lógica de alertas
def check_and_alert(data, ticker):
    data, signals = find_complex_patterns(data)
    
    # Alertas críticas
    alerts = []
    
    if "IHS" in signals:
        alerts.append({
            'level': 'success',
            'icon': '🚀',
            'message': f'Patrón IHS detectado - {signals["IHS"]}'
        })
    
    if "HS" in signals:
        alerts.append({
            'level': 'warning',
            'icon': '⚠️',
            'message': f'Patrón HS detectado - {signals["HS"]}'
        })
    
    for pattern in ["DOJI", "HAMMER", "ENGULFING", "SHOOTINGSTAR"]:
        if pattern in signals:
            alerts.append({
                'level': 'info',
                'icon': '📍',
                'message': f'Patrón de vela: {pattern}'
            })
    
    return alerts

# Mostrar en Streamlit
alerts = check_and_alert(data, ticker)

if alerts:
    st.markdown("### 🚨 Alertas Activas")
    for alert in alerts:
        if alert['level'] == 'success':
            st.success(f"{alert['icon']} {alert['message']}")
        elif alert['level'] == 'warning':
            st.warning(f"{alert['icon']} {alert['message']}")
        else:
            st.info(f"{alert['icon']} {alert['message']}")
else:
    st.info("ℹ️ Sin patrones detectados")
```

---

## Ejemplo 6: Comparación de Múltiples Tickers

```python
import streamlit as st
from src.pattern_recognition import find_complex_patterns
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data

tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
pattern_summary = {}

for ticker in tickers:
    try:
        data = fetch_stock_data(ticker)
        data = process_data(data.reset_index(), ma_window=50)
        data, signals = find_complex_patterns(data)
        
        pattern_summary[ticker] = {
            'IHS': 'IHS' in signals,
            'HS': 'HS' in signals,
            'Patterns': list(signals.keys())
        }
    except Exception as e:
        st.error(f"Error con {ticker}: {e}")

# Mostrar tabla resumen
st.markdown("### 📊 Patrones por Ticker")
for ticker, patterns in pattern_summary.items():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**{ticker}**")
    
    with col2:
        if patterns['IHS']:
            st.success("🚀 IHS")
        elif patterns['HS']:
            st.warning("⚠️ HS")
        else:
            st.info("➖")
    
    with col3:
        st.caption(f"{len(patterns['Patterns'])} patrón(es)")
```

---

## Integración en Dashboard

Para agregar patrones en el dashboard principal:

```python
# En dashboard.py

import streamlit as st
from src.pattern_recognition import find_complex_patterns
from src.visualizations import create_patterns_only_chart

st.markdown("### 🎯 Patrones Técnicos Detectados")

# Mostrar resumen de últimas detecciones
pattern_alerts = [
    ("AAPL", "IHS", "2026-04-25"),
    ("MSFT", "HS", "2026-04-24"),
    ("GOOGL", "HAMMER", "2026-04-23"),
]

for ticker, pattern, date in pattern_alerts:
    if pattern == "IHS":
        st.success(f"🚀 **{ticker}**: {pattern} - {date}")
    elif pattern == "HS":
        st.warning(f"⚠️ **{ticker}**: {pattern} - {date}")
    else:
        st.info(f"📍 **{ticker}**: {pattern} - {date}")
```

---

## Flujo Completo de Uso

```
1. Usuario abre Market Lab
   └─> Selecciona ticker (ej: AAPL)

2. Sistema descarga datos
   └─> Procesa indicadores técnicos

3. Pestaña "Patrones" activada
   └─> Llama find_complex_patterns()

4. Se detectan patrones
   ├─> IHS encontrado
   ├─> MACD patrón detectado
   └─> RSI 14 = 25 (sobreventa)

5. Interfaz muestra alertas
   ├─> 🚀 IHS Detectado (éxito)
   ├─> 💡 Reversión alcista potencial
   └─> [Gráfico con patrones marcados]

6. Usuario toma decisión
   └─> Basada en análisis combinado
```

---

**Notas:**
- Los patrones se detectan automáticamente en cada ejecución
- La tolerancia está configurada en ±5% para mayor confiabilidad
- Combina patrones geométricos con indicadores para mejor confirmación
- Sin overhead computacional significativo
