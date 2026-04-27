# Mejoras de Visualizaciones - Sentinel v2.1

## 📋 Resumen de Cambios

Se han mejorado y ampliado significativamente las funciones de visualización en `src/visualizations.py`. El módulo ahora incluye indicadores técnicos avanzados, gráficos mejorados y nuevas funcionalidades de análisis.

---

## 🔧 Nuevas Funciones de Cálculo de Indicadores

### 1. **calculate_moving_average(data, window=20)**
Calcula el promedio móvil simple (SMA).

```python
data = calculate_moving_average(data, window=50)
# Agrega la columna: data['MA_50']
```

### 2. **calculate_rsi(data, window=14)**
Calcula el Índice de Fuerza Relativa (RSI).

```python
data = calculate_rsi(data, window=14)
# Agrega la columna: data['RSI_14']
```

### 3. **calculate_bollinger_bands(data, window=20, num_std=2)**
Calcula las Bandas de Bollinger con media móvil y desviación estándar.

```python
data = calculate_bollinger_bands(data, window=20)
# Agrega columnas:
# - data['SMA_20']
# - data['STD_20']
# - data['Upper_Band_20']
# - data['Lower_Band_20']
```

### 4. **calculate_macd(data, fast=12, slow=26, signal=9)**
Calcula el MACD (Moving Average Convergence Divergence).

```python
data = calculate_macd(data)
# Agrega columnas:
# - data['EMA_fast']
# - data['EMA_slow']
# - data['MACD']
# - data['Signal_Line']
# - data['MACD_Histogram']
```

---

## 📊 Gráficos Mejorados

### 1. **create_candlestick_chart(data, ticker)**
Candlestick mejorado con múltiples indicadores técnicos.

**Características:**
- Velas de precio verde (alza) y roja (baja)
- SMA 20 y SMA 50
- Bandas de Bollinger
- Leyenda interactiva
- Hover unificado

```python
fig = create_candlestick_chart(processed_data, "AAPL")
st.plotly_chart(fig, use_container_width=True)
```

### 2. **create_moving_average_chart(data, ticker, ma_window=50)**
Comparación de múltiples promedios móviles (20, 50, 200).

```python
fig = create_moving_average_chart(processed_data, "AAPL", ma_window=50)
st.plotly_chart(fig, use_container_width=True)
```

### 3. **create_rsi_chart(data)**
RSI mejorado con niveles de sobrecompra (70) y sobreventa (30).

**Características:**
- Línea de RSI con relleno
- Zonas de sobrecompra/sobreventa claramente marcadas
- Línea media a 50

```python
fig = create_rsi_chart(processed_data)
st.plotly_chart(fig, use_container_width=True)
```

### 4. **create_macd_chart(data)** ⭐ NUEVO
Gráfico completo de MACD con línea de señal e histograma.

**Características:**
- Línea MACD en azul
- Línea de señal en dorado
- Histograma en verde/rojo según divergencia
- Línea de cero para referencia

```python
fig = create_macd_chart(processed_data)
st.plotly_chart(fig, use_container_width=True)
```

### 5. **create_volume_analysis_chart(data)**
Análisis de volumen mejorado con colores dinámicos.

**Características:**
- Barras verdes (cierre arriba) y rojas (cierre abajo)
- Media móvil de 20 días
- Escala automática

```python
fig = create_volume_analysis_chart(processed_data)
st.plotly_chart(fig, use_container_width=True)
```

### 6. **create_daily_returns_histogram(data)**
Distribución de retornos diarios.

```python
fig = create_daily_returns_histogram(processed_data)
st.plotly_chart(fig, use_container_width=True)
```

---

## 🎯 Nuevas Funcionalidades de Análisis

### 1. **score_stock(data, fundamentals=None)** ⭐ NUEVO
Calcula un score de calidad de la acción basado en indicadores técnicos.

```python
score, signals = score_stock(processed_data, fundamentals_dict)
# score: int (0-8)
# signals: list de strings con análisis detallado

# Ejemplo:
# score = 6
# signals = [
#     "✓ Precio por encima de SMA 50",
#     "✓ RSI no sobrecomprado",
#     "✗ RSI sobrevendido",
#     "✓ MACD positivo",
#     "✓ P/E Adelantado < 20 (15.32)",
#     "✓ Deuda/Patrimonio < 1 (0.85)"
# ]
```

**Criterios de scoring:**
- Precio > SMA 50
- RSI < 70 (no sobrecomprado)
- RSI > 30 (no sobrevendido)
- MACD > 0
- P/E Adelantado < 20 (fundamental)
- Deuda/Patrimonio < 1 (fundamental)

### 2. **create_stock_scoring_chart(tickers_scores)** ⭐ NUEVO
Gráfico comparativo del score de múltiples acciones.

```python
tickers_scores = [
    ("AAPL", 7),
    ("MSFT", 5),
    ("GOOGL", 4),
]
fig = create_stock_scoring_chart(tickers_scores)
st.plotly_chart(fig, use_container_width=True)
```

### 3. **create_price_performance_chart(data, ticker)** ⭐ NUEVO
Gráfico dual: Precio vs Retornos Acumulados.

**Características:**
- Eje izquierdo: Precio de cierre
- Eje derecho: Retornos acumulados (%)
- Comparación visual de performance

```python
fig = create_price_performance_chart(processed_data, "AAPL")
st.plotly_chart(fig, use_container_width=True)
```

### 4. **create_correlation_heatmap(data_dict)** ⭐ NUEVO
Matriz de correlación entre múltiples activos.

```python
data_dict = {
    "AAPL": df_aapl,
    "MSFT": df_msft,
    "GOOGL": df_googl,
}
fig = create_correlation_heatmap(data_dict)
st.plotly_chart(fig, use_container_width=True)
```

---

## 🎨 Estilo Visual Consistente

Todos los gráficos utilizan:
- **Template:** plotly_dark (fondo oscuro profesional)
- **Colores primarios:**
  - Verde: #00CC96 (alcista)
  - Rojo: #FF4136 (bajista)
  - Azul: #00B4D8 (indicadores)
  - Dorado: #FFD700 (énfasis)
- **Hover mode:** Unificado (x) para mejor UX
- **Leyendas:** Posicionadas en esquina superior izquierda con fondo semi-transparente

---

## 📈 Ejemplo de Uso Completo

```python
import streamlit as st
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.data_processing import process_data
from src.visualizations import (
    calculate_rsi,
    calculate_macd,
    create_candlestick_chart,
    create_macd_chart,
    create_rsi_chart,
    score_stock
)

# 1. Obtener datos
ticker = "AAPL"
data = fetch_stock_data(ticker)

# 2. Procesar datos
data = process_data(data.reset_index(), ma_window=50)

# 3. Calcular indicadores avanzados
data = calculate_rsi(data)
data = calculate_macd(data)

# 4. Crear visualizaciones
st.plotly_chart(create_candlestick_chart(data, ticker), use_container_width=True)
st.plotly_chart(create_macd_chart(data), use_container_width=True)
st.plotly_chart(create_rsi_chart(data), use_container_width=True)

# 5. Análisis de calidad
score, signals = score_stock(data)
st.metric("Stock Quality Score", f"{score}/8")
st.write("\n".join(signals))
```

---

## ⚠️ Notas Importantes

1. **Requisitos de columnas:** El DataFrame debe tener las columnas: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`

2. **Procesamiento de datos:** Es recomendable usar `process_data()` antes de las visualizaciones para estandarizar el DataFrame

3. **Indicadores automáticos:** Los gráficos crean automáticamente indicadores faltantes si no existen en los datos

4. **Performance:** Para grandes volúmenes de datos (>5000 barras), considere usar una ventana de tiempo más corta

---

## 🔄 Compatibilidad

- ✅ Totalmente compatible con el código existente
- ✅ Puede reemplazar funciones antiguas sin cambios en las llamadas
- ✅ Funciona con Streamlit y Plotly
- ✅ Soporte para datos de yfinance y Alpaca

---

**Última actualización:** 2026-04-25
**Versión:** 2.1
